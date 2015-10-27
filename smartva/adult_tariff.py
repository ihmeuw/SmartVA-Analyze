from __future__ import print_function
from decimal import Decimal

import collections
import csv
import math
import numpy as np
import os
import pickle

from smartva import config
from smartva.adultuniformtrain import FREQUENCIES
from smartva.freetext_vars import ADULT_FREE_TEXT
from smartva.loggers import status_logger, warning_logger
from smartva.tariff_prep import TariffPrep, ScoredVA
from smartva.utils import status_notifier, get_item_count_for_file
from smartva.adult_tariff_data import (
    HCE_DROP_LIST,
    SHORT_FORM_DROP_LIST,
    CAUSES,
    MATERNAL_CAUSES,
    FEMALE_CAUSES,
    MALE_CAUSES,
    AIDS_CAUSES,
    CANCER_CAUSES,
    MALARIA_CAUSES,
    CAUSE_REDUCTION
)

CAUSE_NUM_KEY = 'va46'
CAUSE_NAME_KEY = 'gs_text46'
TARIFF_CAUSE_NUM_KEY = 'xs_name'
MAX_CAUSE_SYMPTOMS = 40
MAX_CAUSE = 46

SID_KEY = 'sid'
AGE_KEY = 'real_age'
SEX_KEY = 'real_gender'


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


class AdultTariff(TariffPrep):
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
        super(AdultTariff, self).__init__(input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form)

        self.AGE_GROUP = 'adult'

    def run(self):
        status_logger.info('Adult :: Processing Adult tariffs')
        status_notifier.update({'progress': 1})

        # Headers are being dropped only from tariff matrix now because of the way we are iterating over the pruned
        # tariffs. It is unnecessary to drop headers from other matrices.
        drop_headers = {TARIFF_CAUSE_NUM_KEY}
        if not self.hce:
            drop_headers.update(HCE_DROP_LIST)
        if not self.free_text:
            drop_headers.update(ADULT_FREE_TEXT)
        if self.short_form:
            drop_headers.update(SHORT_FORM_DROP_LIST)

        with open(os.path.join(config.basedir, '{:s}_cause_names.csv'.format(self.AGE_GROUP)), 'rU') as f:
            reader = csv.DictReader(f)
            cause46_names = {int(cause[CAUSE_NUM_KEY]): cause[CAUSE_NAME_KEY] for cause in reader}

        cause40s = {}

        with open(os.path.join(config.basedir, 'tariffs-{:s}.csv'.format(self.AGE_GROUP)), 'rU') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cause_num = get_cause_num(row[TARIFF_CAUSE_NUM_KEY])

                items = {k: float(v) for k, v in row.items() if k not in drop_headers and not v == '0.0'}.items()
                cause40s[cause_num] = sorted(items, key=lambda _: math.fabs(float(_[1])), reverse=True)[
                                      :MAX_CAUSE_SYMPTOMS]

        va_cause_list = []

        with open(self.input_file_path, 'rb') as f:
            records = get_item_count_for_file(f)
            reader = csv.DictReader(f)
            status_notifier.update({'sub_progress': (0, records)})

            for index, row in enumerate(reader):
                if self.want_abort:
                    return False

                status_notifier.update({'sub_progress': (index,)})

                cause_dict = {}

                for cause, symptoms in cause40s.items():
                    cause_dict[cause] = sum(round5(Decimal(v)) for k, v in symptoms if row[k] == '1')

                va_cause_list.append(ScoredVA(cause_dict, 0, row[SID_KEY], row[AGE_KEY], row[SEX_KEY]))

        status_notifier.update({'sub_progress': None})

        va_validated_cause_list = []

        with open(os.path.join(config.basedir, 'validated-{:s}.csv'.format(self.AGE_GROUP)), 'rU') as f:
            records = get_item_count_for_file(f)
            reader = csv.DictReader(f)
            status_notifier.update({'sub_progress': (0, records)})

            for index, row in enumerate(reader):
                if self.want_abort:
                    return False

                status_notifier.update({'sub_progress': (index,)})

                cause_dict = {}

                for cause, symptoms in cause40s.items():
                    cause_dict[cause] = sum(round5(Decimal(v)) for k, v in symptoms if row[k] == '1')

                va_validated_cause_list.append(ScoredVA(cause_dict, row['va46'], row['sid'], 0, 0))

        status_notifier.update({'sub_progress': None})

        with open(os.path.join(self.intermediate_dir, 'validated-{:s}.pickle'.format(self.AGE_GROUP)), 'wb') as f:
            pickle.dump(va_validated_cause_list, f)
        """
        with open(os.path.join(self.intermediate_dir, 'validated-{:s}.pickle'.format(self.AGE_GROUP)), 'rb') as f:
            va_validated_cause_list = pickle.load(f)
        # """

        uniform_list = []

        for va in va_validated_cause_list:
            uniform_list.extend([va] * FREQUENCIES[va.sid])

        status_logger.info('Adult :: Generating cause rankings.')

        status_notifier.update({'sub_progress': (0, len(va_cause_list))})

        for index, va in enumerate(va_cause_list):
            rank_list = {}

            status_notifier.update({'sub_progress': (index,)})

            for cause in cause40s:
                if self.want_abort:
                    return

                # get the tariff score for this cause for this external VA
                death_score = va.cause_scores[cause]

                # make a list of tariffs of ALL validated VAs for this cause
                sorted_tariffs = sorted((_.cause_scores[cause] for _ in (v_va for v_va in uniform_list)), reverse=True)

                sorted_tariffs = [math.fabs(_ - death_score) for _ in sorted_tariffs]

                rank = np.where(np.array(sorted_tariffs) == min(sorted_tariffs))[0].mean()

                # add 1 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                rank_list[cause] = rank + 1

            va.rank_list = rank_list

        with open(os.path.join(self.intermediate_dir, 'rank_list-adult.pickle'), 'wb') as f:
            pickle.dump(va_cause_list, f)
        """
        with open(os.path.join(self.intermediate_dir, 'rank_list-adult.pickle'), 'rb') as f:
            va_cause_list = pickle.load(f)
        # """

        status_notifier.update({'sub_progress': None})

        rank_list = []
        for va in va_cause_list:
            rank_dict = {"sid": va.sid}
            rank_dict.update(va.rank_list)
            rank_list.append(rank_dict)

        with open(os.path.join(self.intermediate_dir, '{}-external-ranks.csv'.format(self.AGE_GROUP)), 'wb') as f:
            prediction_writer = csv.DictWriter(f, sorted(rank_list[0].keys(), key=lambda x: (isinstance(x, int), x)))
            prediction_writer.writeheader()
            prediction_writer.writerows(rank_list)

        # IDEA - Create a ScoredVA container that does this and other related operations.
        for cause in cause40s:
            cause_list = sorted(uniform_list, key=lambda t: t.cause_scores[cause], reverse=True)
            for i, va in enumerate(cause_list):
                va.rank_list[cause] = i

        status_logger.debug('Adult :: Generating cutoffs')

        with open(os.path.join(self.intermediate_dir, '{}-cutoffs.txt'.format(self.AGE_GROUP)), 'w') as f:
            cutoffs = {}
            for cause_num in sorted(cause40s):
                # Get the uniform list sorted by (reversed) cause_score and sid.
                sorted_cause_list = sorted(uniform_list, key=lambda va: (-va.cause_scores[cause_num], va.sid))

                # Create a list of indexes from the sorted cause list for each cause.
                # we add one because python is 0 indexed and stata is 1 indexed, so this will give us the same
                # numbers as the original stata tool
                local_list = [(i + 1) for i, va in enumerate(sorted_cause_list) if int(va.cause) == cause_num]

                # Find the index of the item at 89%.
                cutoffs[cause_num] = local_list[int(len(local_list) * 0.89)]

                f.write('{} : {}\n'.format(cause_num, cutoffs[cause_num]))

        # The way it was written, the lowest rank is always the length of the uniform list.
        # I am replacing the code to represent that.
        lowest = len(uniform_list)

        # if a VA has a tariff score less than 0 for a certain cause,
        # replace the rank for that cause with the lowest possible rank
        for va in va_cause_list:
            for cause in va.cause_scores:
                if float(va.cause_scores[cause]) < 0.0:
                    va.rank_list[cause] = lowest

        for va in va_cause_list:
            age = int(va.age)
            sex = int(va.gender)

            lowest_cause_list = set()

            # only females ages 15-49 can have anaemia, hemorrhage, hypertensive disease, pregnancy-related, or sepsis
            if sex == 0 or age > 49 or age < 15:
                lowest_cause_list.update(MATERNAL_CAUSES)

            if sex == 1:
                lowest_cause_list.update(FEMALE_CAUSES)

            # female, can't have prostate cancer
            if sex == 2:
                lowest_cause_list.update(MALE_CAUSES)

            # can't have AIDS if over 75
            if age > 75:
                lowest_cause_list.update(AIDS_CAUSES)

            # can't have cancer if under 15
            if age < 15:
                lowest_cause_list.update(CANCER_CAUSES)

            if not self.malaria:
                lowest_cause_list.update(MALARIA_CAUSES)

            for cause_num in cause40s:
                if ((float(va.rank_list[cause_num]) > float(cutoffs[cause_num])) or
                        (float(va.rank_list[cause_num]) > float(len(uniform_list) * .18)) or
                        # EXPERIMENT: reject tariff scores less than a fixed amount as well
                        (float(va.cause_scores[cause_num]) <= 6.0)):
                    lowest_cause_list.add(cause_num)

            for cause_num in lowest_cause_list:
                va.rank_list[cause_num] = lowest

        with open(os.path.join(config.basedir, '{:s}_undetermined_weights-hce{:d}.csv'.format(self.AGE_GROUP, int(self.hce))), 'rU') as f:
            reader = csv.DictReader(f)
            undetermined_matrix = [row for row in reader]

        cause_counts = collections.Counter()
        with open(os.path.join(self.output_dir, '{:s}-predictions.csv'.format(self.AGE_GROUP)), 'wb') as f:
            prediction_writer = csv.writer(f)
            prediction_writer.writerow([SID_KEY, 'cause', 'cause34', 'age', 'sex'])

            for va in va_cause_list:
                cause34 = ''

                va_lowest_rank = min(va.rank_list.values())
                if va_lowest_rank < lowest:
                    multiple = np.extract(np.array(va.rank_list.values()) == va_lowest_rank, va.rank_list.keys())
                    cause34 = CAUSE_REDUCTION[int(multiple[0])]
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
                            if (u_row['sex'] == va.gender and
                                    ((int(va.age) <= int(u_row['age']) < int(va.age) + 5) or
                                        (int(va.age) > 80 and int(u_row['age']) == 80)) and
                                    u_row['iso3'] == self.iso3):
                                # get the value and add it
                                cause_counts.update({u_row['gs_text34']: float(u_row['weight'])})
                else:
                    cause34_name = CAUSES[cause34]
                    cause_counts.update([cause34_name])

                prediction_writer.writerow([va.sid, cause34, cause34_name, va.age, va.gender])

        csmf_writer = csv.writer(open(self.output_dir + os.sep + 'adult-csmf.csv', 'wb'))
        csmf_headers = ["cause", "CSMF"]
        csmf_writer.writerow(csmf_headers)
        for cause_key in cause_counts.keys():
            percent = float(cause_counts[cause_key]) / float(sum(cause_counts.values()))
            csmf_writer.writerow([cause_key, percent])

        # TODO: refactor this test so that it is exercised before
        # merging new pull requests
        # assert int(sum(cause_counts.values())) == len(matrix), \
        #              'CSMF must sum to one'

        prediction_writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-ranks.csv', 'wb'))
        header_row = ["sid"]
        for cause in va_cause_list[0].rank_list.keys():
            header_row.append(cause)
        prediction_writer.writerow(header_row)
        for va in va_cause_list:
            new_row = [va.sid]
            for cause in va.rank_list.keys():
                new_row.append(va.rank_list[cause])
            prediction_writer.writerow(new_row)

        tariff_writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-scores.csv', 'wb'))
        header_row = ["sid"]
        for cause in va_cause_list[0].cause_scores.keys():
            header_row.append(cause)
        tariff_writer.writerow(header_row)
        for va in va_cause_list:
            new_row = [va.sid]
            for cause in va.cause_scores.keys():
                new_row.append(va.cause_scores[cause])
            tariff_writer.writerow(new_row)

    def abort(self):
        self.want_abort = 1


def round5(value):
    return round(value / Decimal(.5)) * .5
