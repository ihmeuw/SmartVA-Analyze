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
    def __init__(self, cause_scores, cause, sid, age, sex, restricted):
        self.cause_scores = cause_scores  # dict of {"cause1" : value, "cause2" :...}
        self.cause = cause  # int
        self.restricted = restricted
        self.rank_list = {}
        self.sid = sid
        self.age = age
        self.sex = sex

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return ('sid={sid} age={age} sex={sex} cause={cause} restricted={restricted}'
                'scores={cause_scores} ranks={rank_list}'.format(**self.__dict__))

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

        cause46_names = self.data_module.CAUSES46

        undetermined_matrix = self._get_undetermined_matrix()

        tariffs = get_tariff_matrix(self.tariffs_filename, drop_headers,
                                    self.data_module.SPURIOUS_ASSOCIATIONS)

        self.cause_list = sorted(tariffs.keys())

        status_logger.info('{:s} :: Generating validated VA cause list.'.format(self.AGE_GROUP.capitalize()))
        validated = self.read_input_file(self.validated_filename)[1]
        validated = self.score_symptom_data(validated, tariffs, 'va46')

        uniform_list = self.generate_uniform_list(validated, self.data_module.FREQUENCIES)

        status_logger.debug('{:s} :: Generating cutoffs'.format(self.AGE_GROUP.capitalize()))
        cutoffs = self.generate_cutoffs(uniform_list, self.data_module.CUTOFF_POS)

        status_logger.info('{:s} :: Generating VA cause list.'.format(self.AGE_GROUP.capitalize()))
        user_data = self.read_input_file(self.input_file_path())[1]
        user_data = self.score_symptom_data(user_data, tariffs,
                                            RULES_CAUSE_NUM_KEY)

        status_logger.info('{:s} :: Generating cause rankings.'.format(self.AGE_GROUP.capitalize()))
        self.generate_cause_rankings(user_data, uniform_list)

        self.write_external_ranks(user_data)

        lowest_rank = len(uniform_list) + 0.5

        self.identify_lowest_ranked_causes(user_data, uniform_list, cutoffs, self.data_module.CAUSE_CONDITIONS,
                                           lowest_rank, self.data_module.UNIFORM_LIST_POS,
                                           self.data_module.MIN_CAUSE_SCORE)

        cause_counts = self.write_predictions(user_data, undetermined_matrix, lowest_rank,
                                              self.data_module.CAUSE_REDUCTION, self.data_module.CAUSES, cause46_names)

        self.write_csmf(cause_counts)

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

    def generate_uniform_list(self, va_cause_list, frequencies):
        """Generate a uniform list of validated Scored VAs from a list of frequencies.

        Args:
            va_cause_list (list): List of validated Scored VAs.
            frequencies (dict): Map of scored VA to frequency.

        Returns:
            list: Uniform list of validated VAs.
        """
        uniform_list = []
        for va in va_cause_list:
            uniform_list.extend([va] * frequencies[va.sid])

        for cause in self.cause_list:
            cause_list = sorted(uniform_list, key=lambda t: t.cause_scores[cause], reverse=True)
            for i, va in enumerate(cause_list):
                va.rank_list[cause] = i

        return uniform_list

    def generate_cutoffs(self, uniform_list, cutoff_pos):
        """Determine cutoff score for each cause. Write scores to a file.

        Args:
            uniform_list (list): Uniform list of validated VAs.
            cutoff_pos (int): Cutoff position.

        Returns:
            dict: Cutoff score for each cause.
        """
        cutoffs = {}
        with open(os.path.join(self.intermediate_dir, '{:s}-cutoffs.txt'.format(self.AGE_GROUP)), 'w') as f:
            for cause_num in self.cause_list:
                self.check_abort()

                # Get the uniform list sorted by (reversed) cause_score and sid.
                sorted_cause_list = sorted(uniform_list, key=lambda va: (-va.cause_scores[cause_num], va.sid))

                # Create a list of indexes from the sorted cause list for each cause.
                # we add one because python is 0 indexed and stata is 1 indexed, so this will give us the same
                # numbers as the original stata tool
                local_list = [(i + 1) for i, va in enumerate(sorted_cause_list) if int(va.cause) == cause_num]

                # Find the index of the item at cutoff position.
                cutoffs[cause_num] = local_list[int(len(local_list) * cutoff_pos)]

                f.write('{} : {}\n'.format(cause_num, cutoffs[cause_num]))

        return cutoffs

    def generate_cause_rankings(self, va_cause_list, uniform_list):
        """Determine cause rankings by comparing
        Args:
            va_cause_list:
            uniform_list:

        Returns:

        """
        status_notifier.update({'sub_progress': (0, len(va_cause_list))})
        cause_scores = {}
        for cause in self.cause_list:
            cause_scores[cause] = sorted((_.cause_scores[cause] for _ in (v_va for v_va in uniform_list)), reverse=True)

        for index, va in enumerate(va_cause_list):
            status_notifier.update({'sub_progress': (index,)})

            for cause in self.cause_list:
                self.check_abort()

                # get the tariff score for this cause for this external VA
                death_score = va.cause_scores[cause]

                lowest_rank = np.sum(np.array(cause_scores[cause]) > death_score)
                highest_rank = len(cause_scores[cause]) - np.sum(np.array(cause_scores[cause]) < death_score)
                avg_rank = (lowest_rank + highest_rank) / 2.

                # add .5 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                # If an observation is scored higher than any observation in the training data it is ranked 0.5
                # If an observation is scored lower than any observation in the training data
                # it is ranked len(training) + 0.5
                va.rank_list[cause] = avg_rank + .5

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
            rank_dict.update(va.rank_list)
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

    def identify_lowest_ranked_causes(self, va_cause_list, uniform_list, cutoffs, cause_conditions, lowest_rank,
                                      uniform_list_pos, min_cause_score):
        """Determine which causes are least likely by testing conditions.
        Only females ages 15-49 can have anaemia, hemorrhage, hypertensive disease, other pregnancy-related, or sepsis.
        Only males can have prostate cancer.
        Eliminate user specified causes (Malaria).

        Args:
            va_cause_list (list): List of Scored VAs.
            uniform_list (list): Uniform list of validated VAs.
            cutoffs (dict): Map of cutoff values for each cause.
            cause_conditions (dict): Conditions necessary for a given list of causes.
            lowest_rank (int): Value to assign to the least likely causes.
            uniform_list_pos (float): Reject causes above this position in the uniform list.
            min_cause_score (float): Reject causes under this threshold.
        """
        for va in va_cause_list:
            self.check_abort()

            # if a VA has a tariff score less than 0 for a certain cause,
            # replace the rank for that cause with the lowest possible rank
            for cause in va.cause_scores:
                if float(va.cause_scores[cause]) < 0.0:
                    va.rank_list[cause] = lowest_rank

            lowest_cause_list = set(va.restricted)

            for condition, causes in cause_conditions.items():
                if not LdapNotationParser(condition, lambda t: value_or_default(va[t], int_or_float), int).evaluate():
                    lowest_cause_list.update(causes)

            if not self.hiv_region:
                lowest_cause_list.update(self.data_module.HIV_CAUSES)

                # This a fragile hack to remove rule-based predictions of AIDS
                # from the child module if the user specifies that the data is
                # from a low prevalence HIV region. It works because the AIDS
                # rule is the last listed rule so it is not masking any other
                # rule-based predictions
                if va.cause in self.data_module.HIV_CAUSES:
                    va.cause = None


            if not self.malaria_region:
                lowest_cause_list.update(self.data_module.MALARIA_CAUSES)

            for cause_num in self.cause_list:
                if ((float(va.rank_list[cause_num]) > float(cutoffs[cause_num])) or
                        (float(va.rank_list[cause_num]) > float(len(uniform_list) * uniform_list_pos)) or
                    # EXPERIMENT: reject tariff scores less than a fixed amount as well
                        (float(va.cause_scores[cause_num]) <= min_cause_score[cause_num])):
                    lowest_cause_list.add(cause_num)

            for cause_num in lowest_cause_list:
                va.rank_list[cause_num] = lowest_rank

    def write_predictions(self, va_cause_list, undetermined_matrix, lowest_rank, cause_reduction, cause34_names, cause46_names):
        """Determine cause predictions and write to a file. Return cause count.

        Args:
            va_cause_list (list): List of Scored VAs.
            undetermined_matrix (list): Matrix of undetermined cause weights.
            lowest_rank (int): Lowest possible rank (highest value, length of uniform list).
            cause_reduction (dict): Map to reduce cause46 values to cause34.
            cause34_names (dict): Cause34 cause names for prediction output.
            cause46_names (dict): Cause46 cause names for warning messages.

        Returns:
            collections.Counter: Dict of cause counts.
        """
        cause_counts = collections.Counter()
        with open(os.path.join(self.output_dir_path, '{:s}-predictions.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY, 'cause', 'cause34', 'age', 'sex'])

            for va in va_cause_list:
                self.check_abort()

                # Record causes already determined.
                cause46 = safe_float(va.cause)
                cause34 = cause_reduction.get(cause46)
                if cause46 and cause34 is None:
                    warning_logger.info(
                        '{group:s} :: SID: {sid:s} was assigned an invalid cause: {cause}'
                        .format(group=self.AGE_GROUP.capitalize(), sid=va.sid, cause=cause46)
                    )

                # If a cause is not yet determined and any cause is higher than the lowest rank:
                va_lowest_rank = min(va.rank_list.values())
                if not cause34 and va_lowest_rank < lowest_rank:
                    # Extract the causes with the highest rank (lowest value). Choose first cause if multiple are found.
                    causes = np.extract(np.array(va.rank_list.values()) == va_lowest_rank, va.rank_list.keys())
                    cause34 = cause_reduction[int(causes[0])]

                    # Warn user if multiple causes are equally likely and which will be chosen.
                    if len(causes) > 1:
                        multiple_cause_list = [cause46_names[int(_)] for _ in causes]
                        warning_logger.info(
                            '{group:s} :: SID: {sid:s} had multiple causes {causes} predicted to be equally likely, '
                            'using \'{causes[0]:s}\'.'.format(group=self.AGE_GROUP.capitalize(), sid=va.sid,
                                                              causes=multiple_cause_list))

                # Count causes, for use in graphs
                cause34_name = cause34_names.get(cause34, 'Undetermined')
                if not cause34:
                    if self.iso3 is None:
                        cause_counts.update([cause34_name])
                    else:
                        # For undetermined, look up the weights for the age and sex category which matches this VA
                        # and add the fractions to the 'count' for all causes. If there is no weight for the
                        # given age-sex, redistribute based on the proporiton across all ages and both sexes. This
                        # may occur if the VA lists an age group in gen_5_4d, but lacks a real age data
                        age = self._calc_age_bin(va.age)
                        try:
                            undetermined_weights = undetermined_matrix[age, va.sex]
                        except KeyError:
                            undetermined_weights = undetermined_matrix[99, 3]
                        cause_counts.update(undetermined_weights)
                else:
                    cause_counts.update([cause34_name])

                # We filled age with a default value of zero but do not want to
                # report this value in output files and graphs
                if float(va.age) == 0 and self.AGE_GROUP in ['adult', 'child']:
                    va.age = ''

                writer.writerow([va.sid, cause34, cause34_name, va.age, va.sex])
        return cause_counts

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
            writer.writerows([[va.sid] + [va.cause_scores[cause] for cause in self.cause_list] for va in va_cause_list])

    def write_tariff_ranks(self, va_cause_list):
        """Write Scored VA Tariff ranks.

        Args:
            va_cause_list (list): List of Scored VAs.
        """
        with open(os.path.join(self.intermediate_dir, '{:s}-tariff-ranks.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY] + self.cause_list)
            writer.writerows([[va.sid] + [va.rank_list[cause] for cause in self.cause_list] for va in va_cause_list])

    def write_csmf(self, cause_counts):
        """Write Scored VA cause counts.

        Args:
            cause_counts (dict): Map of causes to count.
        """
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

        cause_count_values = float(sum(cause_counts.values()))
        with open(os.path.join(self.output_dir_path, '{:s}-csmf.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['cause', 'CSMF'])
            writer.writerows([[k, (v / cause_count_values)] for k, v in cause_counts.items()])
