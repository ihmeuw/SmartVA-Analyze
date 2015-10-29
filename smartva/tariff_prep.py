import collections
import csv
import math
import os
from decimal import Decimal
import numpy as np

from smartva import config
from smartva.adult_tariff_data import MALARIA_CAUSES, CAUSE_REDUCTION, CAUSES
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier, LdapNotationParser

CAUSE_NUM_KEY = 'va46'
CAUSE_NAME_KEY = 'gs_text46'
TARIFF_CAUSE_NUM_KEY = 'xs_name'

MAX_CAUSE_SYMPTOMS = 40

SID_KEY = 'sid'
AGE_KEY = 'real_age'
SEX_KEY = 'real_gender'


def round5(value):
    return round(value / Decimal(.5)) * .5


def get_cause_num(cause):
    return int(cause.lstrip('cause'))


def cmp_rank_keys(a, b):
    """
    Compare rank keys for sorting. Sorts non-causes first, then causes by cause number.

    :param a: Tuple (is cause? (bool), value)
    :param b: Tuple (is cause? (bool), value)
    :return: cmp(a, b)
    """
    # If both values are causes, sort by the cause number.
    if a[0] & b[0]:
        cmp_a, cmp_b = get_cause_num(a[1]), get_cause_num(b[1])
        return cmp(cmp_a, cmp_b)
    return cmp(a, b)


class ScoredVA(object):
    def __init__(self, cause_scores, cause, sid, age, sex):
        # self._backing_dict = {
        #     'sid': sid,
        #     'age': age,
        #     'gender': gender,
        #     'cause': cause,
        #     'cause_scores': cause_scores,
        #     'rank_list': {},
        # }
        self.cause_scores = cause_scores  # dict of {"cause1" : value, "cause2" :...}
        self.cause = cause  # int
        self.rank_list = {}
        self.sid = sid
        self.age = age
        self.sex = sex

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return 'sid={sid} age={age} gender={gender} cs={cause_scores} cause={cause} rl={rank_list}'.format(
            **self.__dict__)

    def __str__(self):
        return self.__repr__()


class TariffPrep(DataPrep):
    def __init__(self, input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form):
        """
        :type input_file: str
        :type output_dir: str
        :type intermediate_dir: str
        :type hce: bool
        :type free_text: bool
        :type malaria: bool
        :type country: str
        :type short_form: bool
        """
        DataPrep.__init__(self, input_file, output_dir, short_form)

        self.intermediate_dir = intermediate_dir

        self.hce = hce
        self.free_text = free_text
        self.malaria = malaria
        self.iso3 = country

        self.cause_list = []

        self.want_abort = False

    @property
    def va_validated_filename(self):
        return os.path.join(config.basedir, 'validated-{:s}.csv'.format(self.AGE_GROUP))

    @property
    def undetermined_matrix_filename(self):
        return os.path.join(config.basedir, '{:s}_undetermined_weights-hce{:d}.csv'.format(self.AGE_GROUP, int(self.hce)))

    def run(self):
        status_logger.info('{:s} :: Processing tariffs'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

    def get_cause46_names(self):
        with open(os.path.join(config.basedir, '{:s}_cause_names.csv'.format(self.AGE_GROUP)), 'rU') as f:
            reader = csv.DictReader(f)
            cause46_names = {int(cause[CAUSE_NUM_KEY]): cause[CAUSE_NAME_KEY] for cause in reader}
        return cause46_names

    def get_cause40s(self, drop_headers):
        cause40s = {}
        with open(os.path.join(config.basedir, 'tariffs-{:s}.csv'.format(self.AGE_GROUP)), 'rU') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cause_num = get_cause_num(row[TARIFF_CAUSE_NUM_KEY])

                items = {k: float(v) for k, v in row.items() if k not in drop_headers and not v == '0.0'}.items()
                cause40s[cause_num] = sorted(items, key=lambda _: math.fabs(float(_[1])), reverse=True)[
                                      :MAX_CAUSE_SYMPTOMS]
        return cause40s

    def get_va_cause_list(self, input_file, cause40s):
        va_cause_list = []
        with open(input_file, 'rb') as f:
            reader = csv.DictReader(f)
            matrix = [row for row in reader]

        status_notifier.update({'sub_progress': (0, len(matrix))})

        for index, row in enumerate(matrix):
            if self.want_abort:
                return False

            status_notifier.update({'sub_progress': (index,)})

            cause_dict = {}

            for cause, symptoms in cause40s.items():
                cause_dict[cause] = sum(round5(Decimal(v)) for k, v in symptoms if row[k] == '1')

            va_cause_list.append(ScoredVA(cause_dict, row.get(CAUSE_NUM_KEY), row[SID_KEY],
                                          row.get(AGE_KEY), row.get(SEX_KEY)))

        status_notifier.update({'sub_progress': None})

        return va_cause_list

    def generate_uniform_list(self, va_cause_list, frequencies):
        uniform_list = []
        for va in va_cause_list:
            uniform_list.extend([va] * frequencies[va.sid])

        for cause in self.cause_list:
            cause_list = sorted(uniform_list, key=lambda t: t.cause_scores[cause], reverse=True)
            for i, va in enumerate(cause_list):
                va.rank_list[cause] = i

        return uniform_list

    def generate_cutoffs(self, uniform_list, cutoff_pos):
        cutoffs = {}
        with open(os.path.join(self.intermediate_dir, '{:s}-cutoffs.txt'.format(self.AGE_GROUP)), 'w') as f:
            for cause_num in self.cause_list:
                # Get the uniform list sorted by (reversed) cause_score and sid.
                sorted_cause_list = sorted(uniform_list, key=lambda va: (-va.cause_scores[cause_num], va.sid))

                # Create a list of indexes from the sorted cause list for each cause.
                # we add one because python is 0 indexed and stata is 1 indexed, so this will give us the same
                # numbers as the original stata tool
                local_list = [(i + 1) for i, va in enumerate(sorted_cause_list) if int(va.cause) == cause_num]

                # Find the index of the item at 89%.
                cutoffs[cause_num] = local_list[int(len(local_list) * cutoff_pos)]

                f.write('{} : {}\n'.format(cause_num, cutoffs[cause_num]))

        return cutoffs

    def generate_cause_rankings(self, va_cause_list, uniform_list):
        status_notifier.update({'sub_progress': (0, len(va_cause_list))})

        for index, va in enumerate(va_cause_list):
            status_notifier.update({'sub_progress': (index,)})

            for cause in self.cause_list:
                if self.want_abort:
                    return

                # get the tariff score for this cause for this external VA
                death_score = va.cause_scores[cause]

                # make a list of tariffs of ALL validated VAs for this cause
                cause_scores = sorted((_.cause_scores[cause] for _ in (v_va for v_va in uniform_list)), reverse=True)

                tariffs = [math.fabs(_ - death_score) for _ in cause_scores]

                # add 1 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                va.rank_list[cause] = (np.where(np.array(tariffs) == min(tariffs))[0].mean()) + 1

        status_notifier.update({'sub_progress': None})

    def write_external_ranks(self, va_cause_list):
        ranks = []
        for va in va_cause_list:
            rank_dict = {"sid": va.sid}
            rank_dict.update(va.rank_list)
            ranks.append(rank_dict)

        with open(os.path.join(self.intermediate_dir, '{:s}-external-ranks.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.DictWriter(f, sorted(ranks[0].keys(), key=lambda x: (isinstance(x, int), x)))
            writer.writeheader()
            writer.writerows(ranks)

    def get_undetermined_matrix(self):
        with open(self.undetermined_matrix_filename, 'rU') as f:
            reader = csv.DictReader(f)
            undetermined_matrix = [row for row in reader]
        return undetermined_matrix

    def identify_lowest_ranked_causes(self, va_cause_list, uniform_list, cutoffs, cause_conditions, lowest_rank,
                                      uniform_list_pos, max_cause_score):
        for va in va_cause_list:
            # if a VA has a tariff score less than 0 for a certain cause,
            # replace the rank for that cause with the lowest possible rank
            for cause in va.cause_scores:
                if float(va.cause_scores[cause]) < 0.0:
                    va.rank_list[cause] = lowest_rank

            lowest_cause_list = set()

            for condition, causes in cause_conditions.items():
                if not LdapNotationParser(condition, lambda t: int(va[t]), int).parse():
                    lowest_cause_list.update(causes)

            if not self.malaria:
                lowest_cause_list.update(MALARIA_CAUSES)

            for cause_num in self.cause_list:
                if ((float(va.rank_list[cause_num]) > float(cutoffs[cause_num])) or
                        (float(va.rank_list[cause_num]) > float(len(uniform_list) * uniform_list_pos)) or
                    # EXPERIMENT: reject tariff scores less than a fixed amount as well
                        (float(va.cause_scores[cause_num]) <= max_cause_score)):
                    lowest_cause_list.add(cause_num)

            for cause_num in lowest_cause_list:
                va.rank_list[cause_num] = lowest_rank

    def write_predictions(self, va_cause_list, undetermined_matrix, lowest_rank, cause_reduction, cause34_names, cause46_names):
        cause_counts = collections.Counter()
        with open(os.path.join(self.output_dir, '{:s}-predictions.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY, 'cause', 'cause34', 'age', 'sex'])

            for va in va_cause_list:
                cause34 = ''

                va_lowest_rank = min(va.rank_list.values())
                if va_lowest_rank < lowest_rank:
                    multiple = np.extract(np.array(va.rank_list.values()) == va_lowest_rank, va.rank_list.keys())
                    cause34 = cause_reduction[int(multiple[0])]
                    if len(multiple) > 1:
                        multiple_cause_list = [cause46_names[int(_)] for _ in multiple]
                        warning_logger.info(
                            '{group:s} :: SID: {sid:s} had multiple causes {causes} predicted to be equally likely, '
                            'using \'{causes[0]:s}\'.'.format(group=self.AGE_GROUP.capitalize(), sid=va.sid,
                                                              causes=multiple_cause_list))

                if not cause34:
                    cause34_name = 'Undetermined'
                    if self.iso3 is None:
                        cause_counts.update([cause34_name])
                    else:
                        # for undetermined, look up the values for each cause using keys (age, sex, country) and
                        # add them to the 'count' for that cause
                        for u_row in undetermined_matrix:
                            if (u_row['iso3'] == self.iso3 and u_row['sex'] == va.sex and
                                    self._matches_undetermined_cause(va, u_row)):
                                cause_counts.update({u_row['gs_text34']: float(u_row['weight'])})

                else:
                    cause34_name = cause34_names[cause34]
                    cause_counts.update([cause34_name])

                writer.writerow([va.sid, cause34, cause34_name, va.age, va.sex])
        return cause_counts

    def _matches_undetermined_cause(self, va, u_row):
        pass

    def write_tariff_scores(self, va_cause_list):
        with open(os.path.join(self.intermediate_dir + os.sep + '{:s}-tariff-scores.csv'.format(self.AGE_GROUP)),
                  'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY] + self.cause_list)
            writer.writerows([[va.sid] + [va.cause_scores[cause] for cause in self.cause_list] for va in va_cause_list])

    def write_tariff_ranks(self, va_cause_list):
        with open(os.path.join(self.intermediate_dir, '{:s}-tariff-ranks.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([SID_KEY] + self.cause_list)
            writer.writerows([[va.sid] + [va.rank_list[cause] for cause in self.cause_list] for va in va_cause_list])

    def write_csmf(self, cause_counts):
        cause_count_values = float(sum(cause_counts.values()))
        with open(os.path.join(self.output_dir, '{:s}-csmf.csv'.format(self.AGE_GROUP)), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['cause', 'CSMF'])
            writer.writerows([[k, (v / cause_count_values)] for k, v in cause_counts.items()])
