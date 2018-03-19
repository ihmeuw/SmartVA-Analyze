from __future__ import division
from bisect import bisect_left, bisect_right
import collections
import csv
import json
import logging
import os

import numpy as np
import xlsxwriter

from smartva import config
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier, LdapNotationParser
from smartva.utils.conversion_utils import value_or_default, safe_float, \
    safe_int
from smartva.utils.utils import int_or_float, UnicodeWriter
from smartva.rules_prep import RULES_CAUSE_NUM_KEY

INPUT_FILENAME_TEMPLATE = '{:s}-symptom.csv'

CAUSE_NAME_KEY = 'gs_text46'
TARIFF_CAUSE_NUM_KEY = 'xs_name'

SID_KEY = 'sid'
AGE_KEY = 'real_age'
SEX_KEY = 'real_gender'


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


def find_key_symptom(tariffs, cause_reduction, cause, endorsements,
                     rules=None):
    """Find the key endorsed symptom for a cause

    Args:
        tariffs (dict): processed tariff matrix
        cause_reduction (dict): mapping from cause46 to cause34
        cause (int): cause number at the cause34 level
        endorsements (iterable): names of endorsed symptoms
        rules (dict): mapping of rule-based cause prediction to key symptom

    Returns:
        symptom (str): name of the key symptom
    """
    rules = rules or {}
    rule_symp = rules.get(cause)
    if rule_symp:
        return rule_symp

    causes46s = [cause46 for cause46, cause34 in cause_reduction.items()
                 if cause34 == cause]
    values = {}
    for cause46 in causes46s:
        for symptom, tariff in tariffs[cause46]:
            if symptom not in endorsements or tariff <= 0:
                continue

            if symptom in values and values[symptom] < tariff:
                continue
            else:
                values[symptom] = tariff

    if values:
        return sorted(values.items(), key=lambda x: x[1])[-1][0]


class Masks(object):
    """Encoding for reason why a cause would be masked.

    CENSORED: causes which are ruled out due to the presence of key symptoms
    EPI: causes ruled out due to user specified epidemiological profile
    DEMOG: causes ruled out due to demographic criteria. Some causes do not
        occur in certain age/sex populations
    OVERALL: causes ranked under the overall percentile
    CAUSE_RANk: causes ranked under the cause-specific percentile
    SCORE: causes scored under the cause-specific minimum score
    """
    CENSORED = 1
    EPI = 2
    DEMOG = 3
    OVERALL = 4
    CAUSE_RANK = 5
    SCORE = 6


class Record(object):
    """Record object for VAs.

    Attributes:
        sid (str): identifier
        age (float): age in years
        sex (int): 1=Male 2=Female
        cause (int): final prediction at cause46 level
        cause34 (int): final prediction at the cause34 level
        cause34_name (str): cause name associated with cause34 prediction
        endorsements (set): names of endorsed symptoms
        censored (list): list of causes which are removed from possible valid
            predictions. These are the result of censoring based on symptom
            endorsements.
        scores (dict): tariff score for each cause
        ranks (dict): rank relative to uniform training data for each cause
        masked (dict): mapping of causes to reason why it is masked
        likelihoods (OrderedDict): mapping of cause34 to categorical likelihood
    """

    def __init__(self, sid=None, age=None, sex=None, cause=0, cause34=None,
                 cause34_name=None, endorsements=None, censored=None,
                 rules=None, scores=None, ranks=None, masked=None,
                 likelihoods=None, predictions34=None):
        self.sid = sid
        self.age = age
        self.sex = sex
        self.cause = cause
        self.cause34 = None
        self.cause34_name = cause34_name
        self.endorsements = endorsements or set()
        self._censored = censored or set()
        self.rules = rules
        self.scores = scores or {}
        self.ranks = ranks or {}
        masked_ = collections.defaultdict(set)
        if censored:
            for cause in censored:
                masked_[cause].add(Masks.CENSORED)
        if masked:
            for cause, removed in masked.items():
                masked_[cause].update(removed)
        self.masked = masked_
        self.likelihoods = likelihoods or {}

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return ('Record(sid={sid}, age={age}, sex={sex}, cause={cause}, '
                'cause34={cause34}, cause34_name={cause34_name}, '
                'censored={_censored}, rules={rules}, scores={scores}, '
                'ranks={ranks}, masked={masked})'.format(**self.__dict__))

    @property
    def censored(self):
        return self._censored

    @censored.setter
    def censored(self, value):
        # TODO: implement removing censored flags from masked if censored
        # is reset and previously censored causes are no longer censored
        try:
            iter(value)
        except TypeError:
            self._censored = {value}
            self.masked[value].add(Masks.CENSORED)
        else:
            self._censored = {x for x in value}
            for cause in value:
                self.masked[cause].add(Masks.CENSORED)


class TariffPrep(DataPrep):
    """Process prepared answers against validated VA data.

    This step accomplishes two main tasks:
        1. prepping the serialized data from fitting tariff
        2. using the model to predict causes for the user data

    The first step includes processing the tariff matrix based on user
    constraints, expanding the training data to a uniform cause distribution,
    and calculating cuttoffs relative to the uniform training data.

    The second step involves score the user data with the tariff matrix,
    ranking it against the training data, removing invalid and improbable
    prediction possibilies, and predicting.

    Notes:
        Processing pipelines must implement `_calc_age_bin` method.
    """

    def __init__(self, data_module, working_dir_path, short_form, options,
                 country):
        super(TariffPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir

        self.hce = options['hce']
        self.free_text = options['free_text']
        self.hiv_region = options['hiv']
        self.malaria_region = options['malaria']
        self.iso3 = country
        self.language = options.get('language', 'english')

        self.cause_list = []

        self.data_module = data_module
        self.AGE_GROUP = data_module.AGE_GROUP

    @property
    def tariffs_filename(self):
        return os.path.join(config.basedir, 'data',
                            'tariffs-{:s}.csv'.format(self.AGE_GROUP))

    @property
    def validated_filename(self):
        return os.path.join(config.basedir, 'data',
                            'validated-{:s}.csv'.format(self.AGE_GROUP))

    @property
    def undetermined_matrix_filename(self):
        filename = '{:s}_undetermined_weights.csv'.format(self.AGE_GROUP)
        return os.path.join(config.basedir, 'data', filename)

    def run(self):
        super(TariffPrep, self).run()

        status_logger.info('{:s} :: Processing tariffs'
                           .format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        # Headers are being dropped only from tariff matrix now because of the
        # way we are iterating over the pruned tariff data. It is unnecessary
        # to drop headers from other matrices.
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

        validated = self.read_input_file(self.validated_filename)[1]

        status_logger.info('{:s} :: Processing validation data.'
                           .format(self.AGE_GROUP.capitalize()))
        train = self.process_training_data(validated, tariffs,
                                           self.data_module.FREQUENCIES,
                                           self.data_module.CUTOFF_POS,
                                           [.25, .5, .75])
        (uniform_train, uniform_scores, uniform_ranks, cutoffs,
         likelihoods) = train

        self.write_cutoffs(cutoffs)

        status_logger.info('{:s} :: Generating VA cause list.'
                           .format(self.AGE_GROUP.capitalize()))
        user_data = self.read_input_file(self.input_file_path())[1]
        user_data = self.score_symptom_data(user_data, tariffs)

        status_logger.info('{:s} :: Generating cause rankings.'
                           .format(self.AGE_GROUP.capitalize()))
        self.generate_cause_rankings(user_data, uniform_scores)

        self.write_intermediate_file(user_data, 'external-ranks', 'ranks')

        lowest_rank = len(uniform_train) + 0.5

        self.mask_ranks(user_data, len(uniform_train), cutoffs,
                        self.data_module.CAUSE_CONDITIONS,
                        lowest_rank, self.data_module.UNIFORM_LIST_POS,
                        self.data_module.MIN_CAUSE_SCORE)

        self.predict(user_data, lowest_rank, self.data_module.CAUSE_REDUCTION,
                     self.data_module.CAUSES, self.data_module.CAUSES46)

        self.determine_likelihood(user_data, likelihoods,
                                  self.data_module.CAUSE_REDUCTION)

        undetermined_weights = self._get_undetermined_matrix()
        csmf, csmf_by_sex = self.calculate_csmf(user_data,
                                                undetermined_weights)

        self.write_predictions(user_data)

        likelihood_names = ['Very Likely', 'Likely', 'Somewhat Likely',
                            'Possible']
        if self.language != 'english':
            path = os.path.join(config.basedir, 'data', '{}.json'.format(self.language))
            with open(path, 'rb') as f:
                translation = json.load(f)
            likelihood_names = [translation['likelihoods'].get(likelihood)
                                for likelihood in likelihood_names]
        else:
            translation = None
        colors = ['#3CB371', '#47d147', '#8ae600', '#e6e600']
        mp = self.write_multiple_predictions_xlsx(user_data, tariffs,
                                                  likelihood_names, colors,
                                                  translation)
        self.write_multiple_predictions_csv(mp)

        self.write_csmf(self.AGE_GROUP, csmf)
        sex_name = {1: 'male', 2: 'female'}
        for sex, csmf_data in csmf_by_sex.items():
            key = '-'.join([self.AGE_GROUP, sex_name[sex]])
            self.write_csmf(key, csmf_data)

        self.write_intermediate_file(user_data, 'tariff-scores', 'scores')

        self.write_intermediate_file(user_data, 'tariff-ranks', 'ranks')

        return user_data

    def score_row(self, row, tariffs):
        """Score a single row of symptom data.

        Calculate the tariff score for each cause by calculating the sum of
        the tariffs for endorsed symptoms.

        Args:
            row (dict): row from symptom data file
            tariffs (dict of lists): processed tariffs by cause

        Returns:
            Record
        """
        drop = {'sid', 'real_age', 'real_gender', 'cause', 'restricted'}
        endorsements = {k for k, v in row.items()
                        if safe_float(v) and k not in drop}
        scores = {}
        for cause, symptoms in tariffs.items():
            scores[cause] = sum(tariff for symptom, tariff in symptoms
                                if symptom in endorsements)
        return Record(sid=row.get(SID_KEY), age=row.get(AGE_KEY),
                      sex=row.get(SEX_KEY), scores=scores,
                      endorsements=endorsements)

    def score_symptom_data(self, symptom_data, tariffs):
        """Score symptom data using a tariffs matrix.

        Args:
            symptom_data (list of dict): symptom data from a csv.DictReader
            tariffs (dict of lists): processed tariffs by cause

        Returns:
            list: List of Scored VAs.
        """
        scored = []

        status_notifier.update({'sub_progress': (0, len(symptom_data))})

        for index, row in enumerate(symptom_data):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            va = self.score_row(row, tariffs)

            va.censored = map(safe_int, row.get('restricted', '').split())
            va.rules = safe_int(row.get(RULES_CAUSE_NUM_KEY))

            scored.append(va)

        status_notifier.update({'sub_progress': None})

        return scored

    def process_training_data(self, train, tariffs, frequencies, cutoff_pos,
                              thresholds):
        """Process the training data.

        The validated data is expanded so that the cause distribution across
        all the observation is uniformly distributed across the causes. The
        sampling frequencies are determined elsewhere and stored in the data
        module.

        Cause-specific cutoffs are calculated as the rank value at the given
        cutoff percentile of the subset of observations whose gold standards
        is the given cause. While the data are sorted also store the
        distribution of scores by cause. This is used to rank the user data.

        Args:
            train (list): List of validated ScoredVAs.
            frequencies (dict): Map of validated sid to frequency.
            cutoff_pos (float): Percentile cutoff from 0 to 1.

        Returns:
            tuple:
                list: validated VAs with uniform cause distribution.
                dict: ordered scores by cause for all VAs in the training data
                dict: mapping of ranks of VAs in the training data for which
                    the gold standard is the given cause
                dict: Cutoff score for each cause.
        """
        uniform_train = []

        status_notifier.update({'sub_progress': (0, 1)})

        for index, row in enumerate(train):
            self.check_abort()

            # Assume half the processing time is scoring/expanding
            # Fill half the status bar based on the number of rows
            status_notifier.update({
                'sub_progress': ((index / 2) / len(train),)
            })

            va = self.score_row(row, tariffs)
            va.cause = row.get('va46')
            uniform_train.extend([va] * frequencies[va.sid])

        scores = {}
        ranks = {}
        cutoffs = {}
        likelihoods = {}

        n_causes = len(self.cause_list)
        n_uniform = len(uniform_train)
        overall_cutoff = n_uniform * self.data_module.CUTOFF_POS

        for index, cause in enumerate(self.cause_list):
            self.check_abort()

            # Assume half the processing time is sorting/ranking
            # Start at 50% and updated in even increments for each cause
            status_notifier.update({
                'sub_progress': (.5 + (index / 2) / n_causes,)
            })

            # Get the uniform training data sorted by (reversed) score and
            # sid. Sorting by sid ensures the ranks are stable between row
            # which have the score but different gold standard causes.
            def sorter(va):
                return -va.scores[cause], va.sid
            uniform_sorted = sorted(uniform_train, key=sorter)

            # Store the scores from the distribution sorted from low to high
            scores[cause] = [va.scores[cause] for va in uniform_sorted][::-1]

            # Determine the rank within the complete uniform training data
            # of the subset of VAs whose gold standard cause is the cause
            # by which the VAs are ranked.
            ranks = [(i + 1) for i, va in enumerate(uniform_sorted)
                     if int(va.cause) == cause]
            n_ranks = len(ranks)
            ranks[cause] = ranks

            # Find the index of the item at cutoff position.
            cutoffs[cause] = ranks[int(n_ranks * cutoff_pos)]

            # Find the rank value at each threshold value
            like = [0]
            like.extend([ranks[int(n_ranks * thre)] for thre in thresholds])
            like.append(min([cutoffs[cause], overall_cutoff]))
            like.append(n_uniform)
            likelihoods[cause] = like

        status_notifier.update({'sub_progress': None})

        return uniform_train, scores, ranks, cutoffs, likelihoods

    def write_cutoffs(self, cutoffs):
        """Write cutoffs to a file.

        Args:
            cutoffs (dict): mapping of cause to cutoff ranks
        """
        output_file = os.path.join(self.intermediate_dir,
                                   '{:s}-cutoffs.txt'.format(self.AGE_GROUP))
        with open(output_file, 'w') as f:
            for cause in self.cause_list:
                f.write('{} : {}\n'.format(cause, cutoffs[cause]))

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
            uniform_scores (dict of lists): sorted distribution of scores
                by cause from uniform training data
        """
        status_notifier.update({'sub_progress': (0, len(scored))})

        for index, va in enumerate(scored):
            status_notifier.update({'sub_progress': (index,)})

            for cause in self.cause_list:
                self.check_abort()

                gt = bisect_left(uniform_scores[cause], va.scores[cause])
                lt = bisect_right(uniform_scores[cause], va.scores[cause])
                avg_rank = len(uniform_scores[cause]) - gt + (gt - lt) / 2.

                va.ranks[cause] = avg_rank + .5

        status_notifier.update({'sub_progress': None})

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

            # Mask based on cause scores
            for cause in va.scores:
                if va.scores[cause] <= min_cause_score[cause]:
                    va.masked[cause].add(Masks.SCORE)

            # Mask based on age/sex criteria
            def lookup(x):
                return value_or_default(va[x], int_or_float)

            for condition, causes in age_sex_restrictions.items():
                if not LdapNotationParser(condition, lookup, int).evaluate():
                    for cause in causes:
                        va.masked[cause].add(Masks.DEMOG)

            # Mask based on regional prevalence of HIV
            if not self.hiv_region:
                for cause in self.data_module.HIV_CAUSES:
                    va.masked[cause].add(Masks.EPI)

            # Mask based on regional prevalence of Malaria
            if not self.malaria_region:
                for cause in self.data_module.MALARIA_CAUSES:
                    va.masked[cause].add(Masks.EPI)

            for cause in self.cause_list:
                # Mask based on cause-specific rank
                if va.ranks[cause] > cause_cutoffs[cause]:
                    va.masked[cause].add(Masks.CAUSE_RANK)

                # Mask based on overall rank
                if va.ranks[cause] > overall_rank_cutoff:
                    va.masked[cause].add(Masks.OVERALL)

            # Apply the mask
            for cause in va.masked:
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
        for i, va in enumerate(user_data):
            self.check_abort()

            # Allow user-specified epidemogical conditions (AIDS or Malaria),
            # age/sex restrictions, and censoring to mask rule-based
            # predictions
            ignore_rules_if = [Masks.EPI, Masks.DEMOG, Masks.CENSORED]
            is_masked = va.masked[va.rules].intersection(ignore_rules_if)

            if va.rules and va.rules in cause46_names and not is_masked:
                va.cause = va.rules
            elif len(set(va.ranks.values())) > 1:
                best_rank = min(va.ranks.values())
                predictions = [cause for cause, rank in va.ranks.items()
                               if rank == best_rank and not va.masked[cause]]

                # Use the first listed cause if there are ties
                if predictions:
                    va.cause = sorted(predictions)[0]

                if len(predictions) > 1:
                    names = [cause46_names[cause] for cause in predictions]
                    msg = ("SID: {} ({} row {}) had multiple causes predicted "
                           "to be equally likely: {}, using first listed."
                           .format(va.sid, self.AGE_GROUP.title(), i, names,
                                   va.cause))
                    warning_logger.info(msg)
                    logging.getLogger('prediction').info(msg)

            va.cause34 = cause_reduction.get(va.cause)
            va.cause34_name = cause34_names.get(va.cause34, 'Undetermined')

    def determine_likelihood(self, user_data, thresholds, cause_reduction):
        """
        """
        for va in user_data:
            self.check_abort()

            # Skip VAs with no predictions, these are undetermined.
            if not va.cause:
                continue

            # Sort the unmasked causes by rank. If there are ties in ranks,
            # causes are sorted in numeric order, which matches the predict
            # method. The true prediction is skipped and inserted into the
            # front of the list. This prevents causes predicted by rules from
            # appearing in multiple places.
            ordered = sorted([(cause, rank) for cause, rank in va.ranks.items()
                              if not va.masked[cause] and cause != va.cause],
                             key=lambda x: (x[1], x[0]))
            ordered.insert(0, (va.cause, va.ranks.get(va.cause)))

            # Keep track of the order of predictions at the cause34 level
            # while looping over cause46 level causes
            pred34 = []

            # Keep track of the likelihoods at the cause34 level while looping
            # over cause46 level causes
            likelihoods = {}

            # The likelihoods should be capped by the previous likelihood
            # This prevents a lower ranked cause from being a more likely
            # prediction
            prev_likelihood = 0
            # import pdb; pdb.set_trace()
            for cause46, rank in ordered:
                cause34 = cause_reduction.get(cause46)
                if cause34 not in pred34:
                    pred34.append(cause34)

                # Give highest likelihood to rule-based predictions
                if cause46 == va.cause == va.rules:
                    likelihood46 = 0
                elif rank >= thresholds[cause46][-1]:
                    # There are `len` -1 ranges between `len` items
                    # ranges are zero-indexed (must substract 2)
                    likelihood46 = len(thresholds[cause46]) - 2
                else:
                    likelihood46 = bisect_right(thresholds[cause46], rank) - 1

                # Use the higher likelihood at the cause34 level, if multiple
                # causes aggregates into same cause
                likelihood34_prev = likelihoods.get(cause34)
                if likelihood34_prev is not None:
                    likelihood34 = min(likelihood46, likelihood34_prev)
                else:
                    likelihood34 = likelihood46

                if likelihood34_prev is None:
                    likelihood34 = max(likelihood34, prev_likelihood)

                prev_likelihood = likelihood34
                likelihoods[cause34] = likelihood34

            likelihoods34 = [(cause, likelihoods[cause]) for cause in pred34]
            va.likelihoods = collections.OrderedDict(likelihoods34)

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
        counts_by_sex = {1: collections.Counter(), 2: collections.Counter()}

        for va in user_data:
            self.check_abort()
            sex = safe_int(va.sex)

            if va.cause34_name == 'Undetermined' and self.iso3:
                age = self._calc_age_bin(va.age)
                try:
                    redistributed = undetermined_weights[age, va.sex]
                except KeyError:
                    redistributed = undetermined_weights[99, 3]
                cause_counts.update(redistributed)
                if sex in counts_by_sex:
                    counts_by_sex[sex].update(redistributed)
            else:
                cause_counts.update([va.cause34_name])
                if sex in counts_by_sex:
                    counts_by_sex[sex].update([va.cause34_name])

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
            for d in (cause_counts, counts_by_sex[1], counts_by_sex[2]):
                if gs_text34 in cause_counts:
                    d.pop(gs_text34)

        # Convert counts to fractions
        total_counts = sum(cause_counts.values())
        csmf = {k: v / total_counts for k, v in cause_counts.items()}

        totals = {sex: sum(counts.values())
                        for sex, counts in counts_by_sex.items()}
        csmf_by_sex = {sex: {k: v / totals[sex] for k, v in counts.items()}
                       for sex, counts in counts_by_sex.items()}

        return csmf, csmf_by_sex

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

    def write_multiple_predictions_xlsx(self, user_data, tariffs,
                                        likelihood_names,
                                        likelihood_colors=None,
                                        translations=None):
        """Write the predicted causes.

        Args:
            user_data (list): List of ScoredVAs with predictions
            tariffs (dict): processed tariff matrix
            likelihood_names (list): Names to use for likelihood categories
                from highest to lowest
            likelihood_colors (list): hex color codes for likelihood categories
                from highest to lowest
        """
        matrix = []   # store data to return
        cause_names = self.data_module.CAUSES
        symptom_descriptions = self.data_module.SYMPTOM_DESCRIPTIONS
        symptom_order = symptom_descriptions.values()
        cause_reduction = self.data_module.CAUSE_REDUCTION
        rule_symptoms = self.data_module.RULE_KEY_SYMPTOMS
        undetermined = 'Undetermined'
        missing = 'Missing'

        likelihood_colors = likelihood_colors or []
        sex_names = {'1': 'Male', '2': 'Female'}

        if translations:
            cause_names = {cause: translations['causes'].get(name, name)
                           for cause, name in self.data_module.CAUSES.items()}
            symptom_descriptions = {
                symp: translations['symptoms'].get(des, des)
                for symp, des in self.data_module.SYMPTOM_DESCRIPTIONS.items()}
            symptom_order = [translations['symptoms'].get(symp, symp)
                             for symp in symptom_order]
            sex_names = {sex: translations['sexes'].get(name, name)
                         for sex, name, in sex_names.items()}
            undetermined = translations['causes'].get(undetermined,
                                                      undetermined)
            missing = translations['sexes'].get(missing, missing)

        n_causes = 3
        headers = ['sid', 'age', 'sex']
        for i in range(1, n_causes + 1):
            headers.extend([
                'cause{}'.format(i),
                'likelihood{}'.format(i),
                'key_symptom{}'.format(i),
            ])
        headers.append('all_symptoms')

        filename = '{:s}-likelihoods.xlsx'.format(self.AGE_GROUP)
        filepath = os.path.join(self.output_dir_path, filename)
        with xlsxwriter.Workbook(filepath) as workbook:
            worksheet = workbook.add_worksheet()

            bold_fmt = workbook.add_format({'bold': True})
            text_wrap_fmt = workbook.add_format({'text_wrap': True})
            text_wrap_vcentered_fmt = workbook.add_format({
                'text_wrap': True,
                'valign': 'vcenter'
            })
            vcentered_fmt = workbook.add_format({'valign': 'vcenter'})

            fill = {}
            for i, like in enumerate(likelihood_names):
                fill[like] = workbook.add_format({
                    'bg_color': likelihood_colors[i],
                    'text_wrap': True,
                    'valign': 'vcenter',
                })

            worksheet.set_row(0, None, bold_fmt)   # headers
            worksheet.freeze_panes(1, 1)   # freeze headers and ID col
            worksheet.set_column(0, 0, 41.00, vcentered_fmt)    # sid
            worksheet.set_column(1, 2, cell_format=vcentered_fmt)    # age/sex

            for c in range(n_causes):
                j = 3 + c * 3
                worksheet.set_column(j, j, 21.86)   # causes
                worksheet.set_column(j + 1, j + 1, 10.29)   # likelihoods
                worksheet.set_column(j + 2, j + 2, 27.29,
                                     text_wrap_vcentered_fmt)   # key symptom

            j = 3 + 3 * n_causes
            worksheet.set_column(j, j, 51.29, text_wrap_fmt)   # key symptoms

            for i, header in enumerate(headers):
                worksheet.write(0, i, header)

            matrix.append(headers)

            for i, va in enumerate(user_data):
                i += 1   # offset for header row
                worksheet.set_row(i, 52.50)   # about 3.5 lines of height

                # TODO: More robust handling of unicode
                try:
                    sid = unicode(va.sid, 'utf-8')
                except UnicodeDecodeError:
                    sid = unicode(va.sid, 'latin-1')

                sex = sex_names.get(va.sex, missing)

                row = [sid, va.age, sex]
                for j, d in enumerate([sid, va.age, sex]):
                    worksheet.write(i, j, d)

                likelihoods = va.likelihoods.items()
                if likelihoods:
                    for c, (cause, likelihood) in enumerate(likelihoods):
                        if c == n_causes:
                            break
                        # Offset 3 demographic columns and previous likelihoods
                        j = 3 + c * 3
                        cause_name = cause_names.get(cause, undetermined)
                        likelihood_name = likelihood_names[likelihood]
                        symptom = find_key_symptom(tariffs, cause_reduction,
                                                   cause, va.endorsements,
                                                   rule_symptoms)
                        symptom_description = symptom_descriptions.get(symptom,
                                                                       '')

                        fmt = fill.get(likelihood_name, vcentered_fmt)

                        worksheet.write(i, j, cause_name, fmt)
                        worksheet.write(i, j + 1, likelihood_name, fmt)
                        worksheet.write(i, j + 2, symptom_description)

                        row.extend([
                            cause_name,
                            likelihood_name,
                            symptom_description
                        ])
                else:
                    worksheet.write(i, 3, undetermined, vcentered_fmt)
                    row.append(undetermined)

                symptoms = sorted([symptom_descriptions[symptom]
                                   for symptom in va.endorsements
                                   if symptom in symptom_descriptions],
                                  key=lambda s: symptom_order.index(s))
                symptoms_list = '\r\n'.join([u'\u2022 {}'.format(symptom)
                                             for symptom in symptoms])
                worksheet.write(i, 3 + n_causes * 3, symptoms_list)

                row.extend([''] * ((3 + n_causes * 3) - len(row)))
                row.append('; '.join(symptoms))
                matrix.append(row)
        return matrix

    def write_multiple_predictions_csv(self, matrix):
        """Write multiple predicted causes with likelihoods.

        The CSV version of this output produces a file which is easily
        machine readable and exists in a non-proprietary format. This allows
        all users to access and post-process this info.

        Args:

        """
        csv_filename = '{:s}-likelihoods.csv'.format(self.AGE_GROUP)
        csv_filepath = os.path.join(self.output_dir_path, csv_filename)
        with open(csv_filepath, 'wb') as f:
            UnicodeWriter(f).writerows(matrix)

    def _calc_age_bin(self, age):
        """Determine the GBD age bin for a given age.

        Ages on the ScoredVA for child and adult modules are in years and the
        ages on the ScoredVA for neonate is in days. Age bins are also not
        evenly spaced. This should be implemented in a module-specific way.

        Args:
            age (float)

        Returns:
            int
        """
        age = float(age)
        # Age may have been filled with the default value of zero
        # In this case do not return an age value. When looking up
        # redistribution weights, the lookup should fail and default all-age
        # both-sex category will be used instead.
        if self.AGE_GROUP == 'neonate':
            if age < 7:
                return 0
            elif 7 <= age <= 28:
                return 7
        else:
            if not age:
                return None
            elif age < 1:
                return 0
            elif 1 <= age < 5:
                return 1
            elif 5 <= age <= 80:
                return int(age / 5) * 5
            elif age > 80:
                return 80

    def write_intermediate_file(self, user_data, name, attr):
        """Write intermediate tariff files.

        Args:
            user_data (list): List of Scored VAs.
        """

        def format_row(va):
            vals = [getattr(va, attr).get(cause) for cause in self.cause_list]
            return [va.sid] + vals

        filename = '{:s}-{}.csv'.format(self.AGE_GROUP, name)
        with open(os.path.join(self.intermediate_dir, filename), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY] + self.cause_list)
            writer.writerows([format_row(va) for va in user_data])

    def write_csmf(self, key, csmf):
        """Write Cause-Specific Mortaility Fractions.

        Args:
            csmf (dict): Map of causes to count.
        """
        filename = '{:s}-csmf.csv'.format(key)
        with open(os.path.join(self.output_dir_path, filename), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['cause', 'CSMF'])
            writer.writerows(sorted(csmf.items(), key=lambda _: _[0]))
