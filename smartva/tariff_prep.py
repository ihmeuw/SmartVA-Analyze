import csv
import math
import os
from decimal import Decimal

from smartva import config
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier

CAUSE_NUM_KEY = 'va46'
CAUSE_NAME_KEY = 'gs_text46'
TARIFF_CAUSE_NUM_KEY = 'xs_name'

MAX_CAUSE_SYMPTOMS = 40
MAX_CAUSE = 46

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
    def __init__(self, cause_scores, cause, sid, age, gender):
        self.cause_scores = cause_scores  # dict of {"cause1" : value, "cause2" :...}
        self.cause = cause  # int
        self.rank_list = {}
        self.sid = sid
        self.age = age
        self.gender = gender

    def __repr__(self):
        return 'sid={sid} age={age} gender={gender} cs={cause_scores} cause={cause} rl={rank_list}'.format(**self.__dict__)

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

        self.want_abort = False

    def run(self):
        status_logger.info('{} :: Processing tariffs'.format(self.AGE_GROUP))
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
            # records = get_item_count_for_file(f)
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
