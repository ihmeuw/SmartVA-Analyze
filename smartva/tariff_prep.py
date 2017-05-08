from __future__ import division
import abc
import collections
import csv
import os

import numpy as np

from smartva import config
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier, LdapNotationParser
from smartva.utils.conversion_utils import value_or_default
from smartva.utils.utils import int_or_float
from smartva.rules_prep import RULES_CAUSE_NUM_KEY

INPUT_FILENAME_TEMPLATE = '{:s}-symptom.csv'

CAUSE_NAME_KEY = 'gs_text46'
TARIFF_CAUSE_NUM_KEY = 'xs_name'

SID_KEY = 'sid'
AGE_KEY = 'real_age'
SEX_KEY = 'real_gender'


def safe_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return 0.0


def safe_int(x):
    return int(safe_float(x))


def clean_tariffs(row, drop_headers=None, spurious=None, max_symptoms=40,
                  precision=0.5):
    """Process the tariffs for a single cause.

    Symptoms are dropped if they appear in the drop list or are spurious.
    The first set include short form, HCE or freetext columns. The second
    set are based on expert review of the tariff matrix. Symptoms with a
    tariff value of zero are also dropped since they do not contribute to
    the scoring. Only the tariffs with the highest magnitude, independent
    of direction are kept. This is done before rounding the tariffs to the
    specified precision. Both rounding and dropping the lowest magnitude
    tariffs guards against overfitting by treating the model fit data as
    a coarse approximation of the results.

    Args:
        row (dict): row of data from tariffs matrix csv
        drop (list of str): symptom names which should be dropped from the
            tariff matrix
        spurious (list of str): cause-specific list of symptom names which
            should be dropped from the tariff matrix
        max_symptoms (int): number of symptoms per cause to keep.
        precision (float): tariffs are rounded to the closest multiple of
            this value.

    Returns:
        list: tuples of (symptom, tariff)
    """
    drop_headers = drop_headers or []
    spurious = spurious or []
    items = [(k, float(v)) for k, v in row.items()
             if k not in drop_headers and k not in spurious and safe_float(v)]
    topN = sorted(items, key=lambda _: abs(_[1]), reverse=True)[:max_symptoms]

    # Use np.round. Round has different behavior in py2 vs py3 for X.5 values
    return [(k, np.round(v / precision) * precision) for k, v in topN]


def get_tariff_matrix(filename, drop_headers, spurious_assoc, max_symptoms=40,
                      precision=0.5):
    """Load the tariff matrix from a csv file.

    Args:
        filename (str): path to the csv file with module-specific tariffs
        drop_headers (list): symptom names which should be dropped from the
            tariff matrix
        spurious_assoc (dict of lists of str): cause-symptom pairs which
            should be dropped from the tariff matrix
        max_symptoms (int): number of symptoms per cause to keep.
        precision (float): tariffs are rounded to the closest multiple of
            this value.

    Returns:
        tariffs (dict): matrix in dict of lists form where keys are causes
            and the list contain tuples of (symptom, tariff)

    See Also:
        clean_tariffs
    """
    tariffs = {}

    with open(filename, 'rU') as f:
        for row in csv.DictReader(f):
            cause_num = int(row[TARIFF_CAUSE_NUM_KEY].lstrip('cause'))
            spurious = spurious_assoc.get(cause_num, [])
            tariffs[cause_num] = clean_tariffs(row, drop_headers, spurious,
                                               max_symptoms, precision)

    return tariffs


class ScoredVA(object):
    def __init__(self, scores=None, cause=0, sid=None, age=None, sex=None,
                 restricted='', ranks=None, cause34=None, cause34_name=None):
        self.scores = scores or {}
        self.cause = cause
        self.restricted = restricted
        self.ranks = ranks or {}
        self.sid = sid
        self.age = age
        self.sex = sex
        self.cause34 = None
        self.cause34_name = None

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return ('sid={sid} age={age} sex={sex} cause={cause} restricted={restricted} '
                'scores={scores} ranks={ranks}'.format(**self.__dict__))

    def __str__(self):
        return self.__repr__()


class TariffPrep(DataPrep):
    """Process prepared answers against validated VA data.

    The main goal of this step is to determine cause of death by comparing symptom scores to those in a uniform list
    of validated VAs.
    Steps to accomplish this goal:
        Read intermediate data file
        Drop answers based on user flags

    Notes:
        Processing pipelines must implement `_matches_undetermined_cause` method.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, working_dir_path, short_form, options, country):
        super(TariffPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir

        self.hce = options['hce']
        self.free_text = options['free_text']
        self.hiv_region = options['hiv']
        self.malaria_region = options['malaria']
        self.iso3 = country

        self.cause_list = []

        self._data_module = None

    @property
    def data_module(self):
        return self._data_module

    @data_module.setter
    def data_module(self, value):
        assert self._data_module is None
        self._data_module = value

        self.AGE_GROUP = self.data_module.AGE_GROUP

    @property
    def tariffs_filename(self):
        return os.path.join(config.basedir, 'data', 'tariffs-{:s}.csv'.format(self.AGE_GROUP))

    @property
    def validated_filename(self):
        return os.path.join(config.basedir, 'data', 'validated-{:s}.csv'.format(self.AGE_GROUP))

    @property
    def undetermined_matrix_filename(self):
        return os.path.join(config.basedir, 'data', '{:s}_undetermined_weights.csv'.format(self.AGE_GROUP))

    @property
    def external_ranks_filename(self):
        return os.path.join(self.intermediate_dir, '{:s}-external-ranks.csv'.format(self.AGE_GROUP))

    def run(self):
        super(TariffPrep, self).run()

        status_logger.info('{:s} :: Processing tariffs'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        # Headers are being dropped only from tariff matrix now because of the way we are iterating over the pruned
        # tariff data. It is unnecessary to drop headers from other matrices.
        drop_headers = {TARIFF_CAUSE_NUM_KEY}
        if not self.hce:
            drop_headers.update(self.data_module.HCE_DROP_LIST)
        if not self.free_text:
            drop_headers.update(self.data_module.FREE_TEXT)
        if self.short_form:
            drop_headers.update(self.data_module.SHORT_FORM_DROP_LIST)

        tariffs = get_tariff_matrix(self.tariffs_filename, drop_headers,
                                    self.data_module.SPURIOUS_ASSOCIATIONS)

        self.cause_list = sorted(tariffs.keys())

        status_logger.info('{:s} :: Generating validated VA cause list.'.format(self.AGE_GROUP.capitalize()))
        validated = self.read_input_file(self.validated_filename)[1]
        validated = self.score_symptom_data(validated, tariffs, 'va46')

        uniform_train = self.generate_uniform_train(validated, self.data_module.FREQUENCIES)

        status_logger.debug('{:s} :: Generating cutoffs'.format(self.AGE_GROUP.capitalize()))
        cutoffs, uniform_scores = self.generate_cutoffs(uniform_train, self.data_module.CUTOFF_POS)

        status_logger.info('{:s} :: Generating VA cause list.'.format(self.AGE_GROUP.capitalize()))
        user_data = self.read_input_file(self.input_file_path())[1]
        user_data = self.score_symptom_data(user_data, tariffs,
                                            RULES_CAUSE_NUM_KEY)

        status_logger.info('{:s} :: Generating cause rankings.'.format(self.AGE_GROUP.capitalize()))
        self.generate_cause_rankings(user_data, uniform_scores)

        self.write_external_ranks(user_data)

        lowest_rank = len(uniform_train) + 0.5

        self.mask_ranks(user_data, len(uniform_train), cutoffs,
                        self.data_module.CAUSE_CONDITIONS,
                        lowest_rank, self.data_module.UNIFORM_LIST_POS,
                        self.data_module.MIN_CAUSE_SCORE)

        self.predict(user_data, lowest_rank, self.data_module.CAUSE_REDUCTION,
                     self.data_module.CAUSES, self.data_module.CAUSES46)

        undetermined_weights = self._get_undetermined_matrix()
        csmf = self.calculate_csmf(user_data, undetermined_weights)

        self.write_predictions(user_data)

        self.write_csmf(csmf)

        self.write_tariff_ranks(user_data)

        self.write_tariff_scores(user_data)

        return user_data

    def score_symptom_data(self, symptom_data, tariffs, cause_key=''):
        """Score symptom data using a tariffs matrix.

        Calculate the tariff score for each cause for every row of symptom
        data by calculating the sum of the tariffs for endorsed symptoms.

        Args:
            symptom_data (list of dict): symptom data from a csv.DictReader
            tariffs (dict of lists): processed tariffs by cause
            cause_key (str): name of column with prediction or gold standard
                cause encoded as an int

        Returns:
            list: List of Scored VAs.
        """
        scored = []

        status_notifier.update({'sub_progress': (0, len(symptom_data))})

        for index, row in enumerate(symptom_data):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            scores = {}

            for cause, symptoms in tariffs.items():
                scores[cause] = sum(tariff for symptom, tariff in symptoms
                                    if safe_float(row.get(symptom)) == 1)

            restricted = map(safe_int, row.get('restricted', '').split())
            cause = safe_int(row.get(cause_key))

            va = ScoredVA(scores, cause, row.get(SID_KEY), row.get(AGE_KEY),
                          row.get(SEX_KEY), restricted)
            scored.append(va)

        status_notifier.update({'sub_progress': None})

        return scored

    def generate_uniform_train(self, scored, frequencies):
        """Expand a matrix ScoredVAs using predetermined frequencies.

        The validated data is expanded so that the cause distribution across
        all the observation is uniformly distributed across the causes. The
        sampling frequencies are determined elsewhere and stored.

        Args:
            scored (list): List of validated ScoredVAs.
            frequencies (dict): Map of validated sid to frequency.

        Returns:
            list: validated VAs with uniform cause distribution.
        """
        uniform_train = []
        for va in scored:
            uniform_train.extend([va] * frequencies[va.sid])

        return uniform_train

    def generate_cutoffs(self, uniform_train, cutoff_pos):
        """Determine cutoff rank for each cause. Write cutoffs to a file.

        Args:
            uniform_train (list): Uniform list of validated VAs.
            cutoff_pos (int): Cutoff position.

        Returns:
            dict: Cutoff score for each cause.
        """
        cutoffs = {}
        uniform_scores = {}
        output_file = os.path.join(self.intermediate_dir,
                                   '{:s}-cutoffs.txt'.format(self.AGE_GROUP))
        with open(output_file, 'w') as f:
            for cause in self.cause_list:
                self.check_abort()

                # Get the uniform training data sorted by (reversed) score and
                # sid. Sorting by sid ensures the ranks are stable between row
                # which have the score but different gold standard causes.
                def sorter(va):
                    return -va.scores[cause], va.sid
                uniform_sorted = sorted(uniform_train, key=sorter)

                # Determine the rank within the complete uniform training data
                # of the subset of VAs whose gold standard cause is the cause
                # by which the VAs are ranked.
                ranks = [(i + 1) for i, va in enumerate(uniform_sorted)
                         if int(va.cause) == cause]

                # Find the index of the item at cutoff position.
                cutoffs[cause] = ranks[int(len(ranks) * cutoff_pos)]

                f.write('{} : {}\n'.format(cause, cutoffs[cause]))

                # Store the scores from the sorted distribution
                uniform_scores[cause] = np.array([va.scores[cause]
                                                  for va in uniform_sorted])

        return cutoffs, uniform_scores

    def generate_cause_rankings(self, scored, uniform_scores):
        """Determine rank for each cause.

        The scored user data is ranked against the scores from the validation
        data which has been resampled to a uniform cause distribtuion. If an
        observation is scored higher than any observation in the training data
        it is ranked 0.5. If an observation is scored lower than any
        observation in the training data it is ranked len(training) + 0.5.

        The user_data is modified in place and not returned.

        Args:
            scored (list): list of ScoredVAs from user data
            uniform_scores (dict of np.array): sorted distribution of scores
                by cause from uniform training data
        """
        status_notifier.update({'sub_progress': (0, len(scored))})

        for index, va in enumerate(scored):
            status_notifier.update({'sub_progress': (index,)})

            for cause in self.cause_list:
                self.check_abort()

                gt = np.sum(uniform_scores[cause] > va.scores[cause])
                lt = np.sum(uniform_scores[cause] < va.scores[cause])
                total = uniform_scores[cause].shape[0]
                avg_rank = (gt + total - lt) / 2.

                va.ranks[cause] = avg_rank + .5

        status_notifier.update({'sub_progress': None})

    def write_external_ranks(self, va_cause_list):
        """Write Scored VA ranks to a file.

        Args:
            va_cause_list (list): List of Scored VAs.
        """
        ranks = []
        for va in va_cause_list:
            self.check_abort()

            rank_dict = {"sid": va.sid}
            rank_dict.update(va.ranks)
            ranks.append(rank_dict)

        DataPrep.write_output_file(sorted(ranks[0].keys(), key=lambda x: (isinstance(x, int), x)),
                                   ranks,
                                   self.external_ranks_filename)

    def _get_undetermined_matrix(self):
        """Return mapping of undetermined weights read from the specified file.

        The undetermined weights files are module specific and contains columns
        for age, sex, iso3 and cause (coded as gs_text34). There are a multiple
        columns for different weights. The weights vary by the predictive
        accuracy of a given parameter set on the gold standard data. We vary
        the instrument (short vs full) and whether HCE columns are used, which
        gives us four sets of weights

        Returns:
            dict: Undetermined weights data. Keys are (age, sex) and values
                a dict of cause -> weight
        """
        # Only read in the csv file if it is going to be used
        # If self.iso3 is None, Undetermined CMSF is not redistributed
        weights = {}
        if self.iso3:
            # Determine which set of weights to use
            instrument = 'short' if self.short_form else 'full'
            weight_key = '{}_hce{}'.format(instrument, int(self.hce))

            with open(self.undetermined_matrix_filename, 'rU') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Only use rows for the specified country
                    if row['iso3'] != self.iso3:
                        continue

                    age = int(row['age'])
                    sex = int(row['sex'])
                    cause = row['gs_text34']
                    if (age, sex) not in weights:
                        weights[age, sex] = {}
                    weights[age, sex][cause] = float(row[weight_key])

        return weights

    def mask_ranks(self, user_data, n_uniform_train, cause_cutoffs,
                   age_sex_restrictions, lowest_rank, overall_rank_cutoff,
                   min_cause_score):
        """Mask the ranks for some causes based on certain criteria.

        Causes may by masked for any of the following reasons:
        * The is biologically impossible/improbably given the age and sex of
          the decent. Example: no prostate cancer in females.
        * User data may come from areas with very low prevalence of certain
          infectious diseases which are not likely to occur in the sample.
          These are indicated by the HIV and Malaria options flags.
        * The tariff score for a cause may be below the minimum score.
        * The rank for a cause may be below the cause-specific minimum rank.
        * The rank for a cause may be below the minimum overall rank.

        The last three are information criteria which prevent unstable
        predictions for VAs with very few endorsements or only endorsements
        which do not clearly lead to a given prediction.

        This modifies the records in place and does not return anything.

        Args:
            user_data (list): List of Scored VAs.
            n_uniform_train (int): number of observations in the validated
                data which has been resampled to a uniform cause distribution.
            cause_cutoffs (dict): Map of cutoff ranks for each cause.
            age_sex_restrictions (dict): Conditions necessary for a given
                list of causes. Keys are LDAP strings which compare age or
                sex to a numeric threshold.
            lowest_rank (int): Value to assign to the least likely causes.
            overall_rank_cutoff (float): The percentile (between 0 and 1)
                under which a cause is rejected
            min_cause_score (dict): Map of cutoff scores for each cause.
        """
        overall_rank_cutoff = n_uniform_train * overall_rank_cutoff
        for va in user_data:
            self.check_abort()

            # Collect a set of causes which should be masked for this VA
            masked = set(va.restricted)

            # Mask based on cause scores
            for cause in va.scores:
                if va.scores[cause] <= min_cause_score[cause]:
                    masked.add(cause)

            # Mask based on age/sex criteria
            def lookup(x):
                return value_or_default(va[x], int_or_float)

            for condition, causes in age_sex_restrictions.items():
                if not LdapNotationParser(condition, lookup, int).evaluate():
                    masked.update(causes)

            # Mask based on regional prevalence of HIV
            if not self.hiv_region:
                masked.update(self.data_module.HIV_CAUSES)

                # This a fragile hack to remove rule-based predictions of AIDS
                # from the child module if the user specifies that the data is
                # from a low prevalence HIV region. It works because the AIDS
                # rule is the last listed rule so it is not masking any other
                # rule-based predictions
                if va.cause in self.data_module.HIV_CAUSES:
                    va.cause = None

            # Mask based on regional prevalence of Malaria
            if not self.malaria_region:
                masked.update(self.data_module.MALARIA_CAUSES)

            for cause in self.cause_list:
                # Mask based on cause-specific rank
                if va.ranks[cause] > cause_cutoffs[cause]:
                    masked.add(cause)

                # Mask based on overall rank
                if va.ranks[cause] > overall_rank_cutoff:
                    masked.add(cause)

            # Apply the mask
            for cause in masked:
                va.ranks[cause] = lowest_rank

    def predict(self, user_data, lowest_rank, cause_reduction, cause34_names,
                cause46_names):
        """Determine cause predictions.

        First look for causes which are already specified. These are rule
        based predictions. If this is missing or invalid predictions are
        based on the tariff ranks.

        This modifies a list in place and adds the cause34 and cause34_name
        attributes to the ScoredVA objects.

        Args:
            user_data (list): list of ScoredVAs which have been ranked.
            lowest_rank (int): Lowest possible rank.
            cause_reduction (dict): Map to reduce cause46 values to cause34.
            cause34_names (dict): Cause34 cause names for prediction output.
            cause46_names (dict): Cause46 cause names for warning messages.
        """
        for va in user_data:
            self.check_abort()

            # Record the cause if it is already determined
            cause34 = cause_reduction.get(va.cause)
            if cause34 is None:
                warning_logger.debug(
                    '{group:s} :: SID: {sid:s} was assigned an invalid '
                    'cause: {cause}'.format(group=self.AGE_GROUP.capitalize(),
                                            sid=va.sid, cause=va.cause)
                )

            # Use tariff prediction if the cause is either missing or invalid
            best_rank_value = min(va.ranks.values() or [0])
            if not cause34 and best_rank_value < lowest_rank:
                predictions = [cause for cause, rank in va.ranks.items()
                               if rank == best_rank_value]

                # Use the first listed cause if there are ties
                cause34 = cause_reduction[sorted(predictions)[0]]

                if len(predictions) > 1:
                    names = [cause46_names[cause] for cause in predictions]
                    warning_logger.info(
                        '{group:s} :: SID: {sid:s} had multiple causes '
                        '{causes} predicted to be equally likely, using '
                        '\'{causes[0]:s}\'.'
                        .format(group=self.AGE_GROUP.capitalize(),
                                sid=va.sid, causes=names)
                    )

            va.cause34 = cause34
            va.cause34_name = cause34_names.get(cause34, 'Undetermined')

    def calculate_csmf(self, user_data, undetermined_weights):
        """Tabluate predictions into Cause-Specific Mortality Fractions.

        If a country is specified the undetermined predictions will be
        redistributed. The weights are by the Global Burden of Disease age,
        sex, country and cause34. For each undetermined prediction, a
        fractions will be added to the 'count' for all relevant causes. If
        there is no weight for the given age-sex, it will be redistributed
        based on the proporiton across all ages and both sexes. This
        may occur if age or sex data is missing such as when the VA lists an
        age group in gen_5_4d, but lacks a real age data.

        Args:
            user_data (list): list of ScoredVAs with predictions
            undetermined_weights: redistribution weights by age and sex
        """
        cause_counts = collections.Counter()

        for va in user_data:
            self.check_abort()

            if va.cause34_name == 'Undetermined' and self.iso3:
                age = self._calc_age_bin(va.age)
                try:
                    redistributed = undetermined_weights[age, va.sex]
                except KeyError:
                    redistributed = undetermined_weights[99, 3]
                cause_counts.update(redistributed)
            else:
                cause_counts.update([va.cause34_name])

        # The undetermined weights may have redistributed onto causes which
        # the user specified as non-existent. These should be removed.
        drop_causes = []
        if not self.hiv_region:
            drop_causes.extend(self.data_module.HIV_CAUSES)
        if not self.malaria_region:
            drop_causes.extend(self.data_module.MALARIA_CAUSES)

        for cause in drop_causes:
            cause34 = self.data_module.CAUSE_REDUCTION[cause]
            gs_text34 = self.data_module.CAUSES[cause34]
            if gs_text34 in cause_counts:
                cause_counts.pop(gs_text34)

        # Convert counts to fractions
        total_counts = sum(cause_counts.values())
        csmf = {k: v / total_counts for k, v in cause_counts.items()}

        return csmf

    def write_predictions(self, user_data):
        """Write the predicted causes.

        Args:
            user_data (list): List of ScoredVAs with predictions
        """
        def format_row(va):
            # We filled age with a default value of zero but do not want to
            # report this value in output files and graphs
            if float(va.age) == 0 and self.AGE_GROUP in ['adult', 'child']:
                va.age = ''
            return [va.sid, va.cause34, va.cause34_name, va.age, va.sex]

        filename = '{:s}-predictions.csv'.format(self.AGE_GROUP)
        with open(os.path.join(self.output_dir_path, filename), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY, 'cause', 'cause34', 'age', 'sex'])
            writer.writerows([format_row(va) for va in user_data])

    @abc.abstractmethod
    def _calc_age_bin(self, va, u_row):
        """Determine the GBD age bin for a given age.

        Ages on the ScoredVA for child and adult modules are in years and the
        ages on the ScoredVA for neonate is in days. Age bins are also not
        evenly spaced. This should be implemented in a module-specific way.

        Args:
            age (float)

        Returns:
            int
        """
        pass

    def write_tariff_scores(self, va_cause_list):
        """Write Scored VA Tariff scores.

        Args:
            va_cause_list (list): List of Scored VAs.
        """
        with open(os.path.join(self.intermediate_dir, '{:s}-tariff-scores.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY] + self.cause_list)
            writer.writerows([[va.sid] + [va.scores[cause] for cause in self.cause_list] for va in va_cause_list])

    def write_tariff_ranks(self, va_cause_list):
        """Write Scored VA Tariff ranks.

        Args:
            va_cause_list (list): List of Scored VAs.
        """
        with open(os.path.join(self.intermediate_dir, '{:s}-tariff-ranks.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY] + self.cause_list)
            writer.writerows([[va.sid] + [va.ranks[cause] for cause in self.cause_list] for va in va_cause_list])

    def write_csmf(self, csmf):
        """Write Cause-Specific Mortaility Fractions.

        Args:
            csmf (dict): Map of causes to count.
        """
        filename = '{:s}-csmf.csv'.format(self.AGE_GROUP)
        with open(os.path.join(self.output_dir_path, filename), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['cause', 'CSMF'])
            writer.writerows(sorted(csmf.items(), key=lambda _: _[0]))
