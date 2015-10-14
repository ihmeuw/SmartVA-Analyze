from __future__ import print_function
import csv
from decimal import Decimal
import math
import os
import pickle
import numpy as np

from smartva import config
from smartva.adultuniformtrain import FREQUENCIES
from smartva.data_prep import DataPrep
from smartva.freetext_vars import ADULT_FREE_TEXT
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier, get_item_count_for_file
from smartva.adult_tariff_data import (
    ADULT_HCE_DROP_LIST,
    ADULT_SHORT_FORM_DROP_LIST,
    ADULT_CAUSES
)

VALIDATED_CAUSE_NUMBER = 'va46'
MAX_CAUSE_SYMPTOMS = 40
MAX_CAUSE = 46


# data structure we use to keep track of an manipulate data
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


class Tariff(DataPrep):
    AGE_GROUP = 'adult'

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
        status_logger.info('Adult :: Processing Adult tariffs')
        status_notifier.update({'progress': (4,)})

        writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-results.csv', 'wb', buffering=0))

        drop_headers = set()
        if not self.hce:
            drop_headers.update(ADULT_HCE_DROP_LIST)
        if not self.free_text:
            drop_headers.update(ADULT_FREE_TEXT)
        if self.short_form:
            drop_headers.update(ADULT_SHORT_FORM_DROP_LIST)

        cause40s = {}

        with open(os.path.join(config.basedir, 'tariffs-{:s}.csv'.format(self.AGE_GROUP)), 'rU') as f:
            reader = csv.DictReader(f)

            drop_headers.add('xs_name')

            for row in reader:
                items = {k: float(v) for k, v in row.items() if k not in drop_headers and not v == '0.0'}.items()
                cause40s[row['xs_name']] = sorted(items, key=lambda _: math.fabs(float(_[1])), reverse=True)[
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

                va_cause_list.append(ScoredVA(cause_dict, 0, row['sid'], row['real_age'], row['real_gender']))

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

        """

        with open(os.path.join(config.basedir, 'validated-{:s}.pickle'.format(self.AGE_GROUP)), 'rb') as f:
            p = pickle.Unpickler(f)
            va_validated_cause_list = p.load()

        """

        uniform_list = []

        for va in va_validated_cause_list:
            uniform_list.extend([va] * FREQUENCIES[va.sid])

        status_logger.debug('Adult :: Generating cause rankings.')

        status_notifier.update({'sub_progress': (0, len(va_cause_list))})

        for index, va in enumerate(va_cause_list):
            rank_list = {}
            for cause in cause40s:
                if self.want_abort:
                    return

                status_notifier.update({'sub_progress': (index,)})

                # get the tariff score for this cause for this external VA
                death_score = va.cause_scores[cause]
                # make a list of tariffs of ALL validated VAs for this cause
                sorted_tariffs = sorted((x.cause_scores[cause] for x in (v_va for v_va in uniform_list)), reverse=True)

                sorted_tariffs = [math.fabs(x - death_score) for x in sorted_tariffs]

                rank = np.where(np.array(sorted_tariffs) == min(sorted_tariffs))[0].mean()

                # add 1 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                rank_list[cause] = rank + 1

            va.rank_list = rank_list
            # print(va.sid, rank_list)

        status_notifier.update({'sub_progress': None})

        rank_writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-external-ranks.csv', 'wb', buffering=0))
        header_row = ["sid"]
        for cause in va_cause_list[0].rank_list.keys():
            header_row.append(cause)
        rank_writer.writerow(header_row)
        for va in va_cause_list:
            new_row = [va.sid]
            for cause in va.rank_list.keys():
                new_row.append(va.rank_list[cause])
            rank_writer.writerow(new_row)

        for i in range(1, 47):
            cause = "cause" + str(i)
            cause_list = []
            for va in uniform_list:
                cause_list.append([va.sid, va.cause_scores[cause], va])
            sorted_cause_list = sorted(cause_list, key=lambda t: t[1], reverse=True)
            # now have a sorted list of sid, cause_score for a specific cause
            for j, item in enumerate(sorted_cause_list):
                item[2].rank_list[cause] = j

        status_logger.debug('Adult :: Generating cutoffs')

        cutoffs = []
        for i in range(1, 47):
            cause_list = []
            for va in uniform_list:
                cause_list.append([va.cause, va.cause_scores["cause" + str(i)], va.sid, va])

            cause_list.sort(key=lambda t: t[2])
            cause_list.sort(key=lambda t: t[1], reverse=True)
            sorted_list = cause_list

            local_list = []
            for j, va in enumerate(sorted_list):
                if va[0] == str(i):
                    # we add one because python is 0 indexed and stata is 1 indexed, so this will give us the same
                    # numbers as the original stata tool
                    local_list.append(j + 1)

            # make it an int, don't round
            index = int(len(local_list) * .89)
            cutoffs.append(local_list[index])

        f = open(self.intermediate_dir + os.sep + 'adult-cutoffs.txt', 'w')
        for i, cutoff in enumerate(cutoffs):
            f.write(str(i + 1) + " : " + str(cutoff) + "\n")
        f.close()

        # lowest rank is actually the biggest number
        lowest = 0
        # find the lowest rank and then add 1 to it
        for va in va_cause_list:
            for cause in va.rank_list.keys():
                if float(va.rank_list[cause]) > 0 and float(va.rank_list[cause]) > lowest:
                    lowest = float(va.rank_list[cause])
        lowest += 1

        # if a VA has a tariff score less than 0 for a certain cause,
        # replace the rank for that cause with the lowest possible rank
        for va in va_cause_list:
            for cause in va.cause_scores.keys():
                if float(va.cause_scores[cause]) < 0:
                    va.rank_list[cause] = lowest

        for i, row in enumerate(matrix):
            age = int(row[headers.index('real_age')])
            sex = int(row[headers.index('real_gender')])

            # only females ages 15-49 can have anaemia, hemorrhage, hypertensive disease, other pregnancy-related, or sepsis
            maternal_causes = [3, 20, 22, 36, 42]
            rankings_row = va_cause_list[i].rank_list

            if sex == 0 or age > 49 or age < 15:
                for cause in maternal_causes:
                    rankings_row["cause" + str(cause)] = lowest

            female_causes = [6, 7]
            if sex == 0:
                for cause in female_causes:
                    rankings_row["cause" + str(cause)] = lowest

            # female, can't have prostate cancer
            if sex == 1:
                rankings_row["cause39"] = lowest

            # can't have AIDS if over 75
            if age > 75:
                rankings_row["cause1"] = lowest
                rankings_row["cause2"] = lowest

            # can't have cancer if under 15
            cancers = [6, 7, 9, 17, 27, 30, 39, 43]
            if age < 15:
                for cause in cancers:
                    rankings_row["cause" + str(cause)] = lowest

            if not self.malaria:
                rankings_row["cause29"] = lowest

        for va in va_cause_list:
            for i in range(1, 47):
                if float(va.rank_list["cause" + str(i)]) > float(cutoffs[i - 1]):
                    va.rank_list["cause" + str(i)] = lowest
                elif float(va.rank_list["cause" + str(i)]) > float(len(uniform_list) * .18):
                    va.rank_list["cause" + str(i)] = lowest
                elif float(va.cause_scores["cause" + str(
                        i)]) <= 6.0:  # EXPERIMENT: reject tariff scores less than a fixed amount as well
                    va.rank_list["cause" + str(i)] = lowest

        # changing 46 causes to 34 causes:
        cause_reduction = {'cause1': '1', 'cause2': '1', 'cause3': '21', 'cause4': '2', 'cause5': '3', 'cause6': '4',
                           'cause7': '5', 'cause8': '6', 'cause9': '7', 'cause10': '8', 'cause11': '9', 'cause12': '9',
                           'cause13': '9', 'cause14': '10', 'cause15': '11', 'cause16': '12', 'cause17': '13',
                           'cause18': '14', 'cause19': '15', 'cause20': '21', 'cause21': '16', 'cause22': '21',
                           'cause23': '17', 'cause24': '22', 'cause25': '22', 'cause26': '18', 'cause27': '19',
                           'cause28': '18', 'cause29': '20', 'cause30': '25', 'cause31': '22', 'cause32': '25',
                           'cause33': '23', 'cause34': '24', 'cause35': '25', 'cause36': '21', 'cause37': '26',
                           'cause38': '27', 'cause39': '28', 'cause40': '29', 'cause41': '30', 'cause42': '21',
                           'cause43': '31', 'cause44': '32', 'cause45': '33', 'cause46': '34', 'Undetermined': ''}

        cause_counts = {}
        rank_writer = csv.writer(open(self.output_dir + os.sep + 'adult-predictions.csv', 'wb', buffering=0))
        rank_writer.writerow(['sid', 'cause', 'cause34', 'age', 'sex'])
        for va in va_cause_list:
            cause_score = lowest
            real_cause = 'Undetermined'
            cause34 = ''
            multiple = {}
            for cause in va.rank_list:
                if float(va.rank_list[cause]) < cause_score:
                    cause_score = float(va.rank_list[cause])
                    real_cause = cause
                    cause34 = cause_reduction[cause]
                    multiple[va.sid] = [cause]
                elif cause_score == float(va.rank_list[cause]) and cause_score != lowest:
                    multiple[va.sid].append(cause)

            # Notify user if multiple causes have been determined.
            for sid_key, causes in multiple.items():
                if len(causes) > 1:
                    warning_logger.info(
                        '{group:s} :: VA {sid:s} had multiple matching results {causes}, using {causes[0]}'.format(
                            group=self.AGE_GROUP.capitalize(), sid=sid_key, causes=causes))

            if cause34 == '':
                cause34 = 'Undetermined'
                if self.iso3 is None:
                    if cause34 in cause_counts.keys():
                        cause_counts[cause34] += 1.0
                    else:
                        cause_counts[cause34] = 1.0
                else:
                    # for undetermined, look up the values for each cause using keys (age, sex, country) and
                    # add them to the 'count' for that cause
                    determined = 0
                    undetermined = 0
                    for uRow in undetermined_matrix:
                        if uRow[undetermined_headers.index('sex')] == va.gender and ((int(va.age) <= int(uRow[undetermined_headers.index('age')]) < int(va.age) + 5) or (int(va.age) > 80 and int(uRow[undetermined_headers.index('age')]) == 80)) and uRow[undetermined_headers.index('iso3')] == self.iso3:
                            # get the value and add it
                            if uRow[undetermined_headers.index('gs_text34')] in cause_counts.keys():
                                cause_counts[uRow[undetermined_headers.index('gs_text34')]] += float(
                                    uRow[undetermined_headers.index('weight')])
                            else:
                                cause_counts[uRow[undetermined_headers.index('gs_text34')]] = float(
                                    uRow[undetermined_headers.index('weight')])
            else:
                cause34 = ADULT_CAUSES[cause34]
                if cause34 in cause_counts.keys():
                    cause_counts[cause34] += 1.0
                else:
                    cause_counts[cause34] = 1.0
            rank_writer.writerow([va.sid, cause_reduction[real_cause], cause34, va.age, va.gender])

        csmf_writer = csv.writer(open(self.output_dir + os.sep + 'adult-csmf.csv', 'wb', buffering=0))
        csmf_headers = ["cause", "CSMF"]
        csmf_writer.writerow(csmf_headers)
        for cause_key in cause_counts.keys():
            percent = float(cause_counts[cause_key]) / float(sum(cause_counts.values()))
            csmf_writer.writerow([cause_key, percent])

        # TODO: refactor this test so that it is exercised before
        # merging new pull requests
        # assert int(sum(cause_counts.values())) == len(matrix), \
        #              'CSMF must sum to one'

        rank_writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-ranks.csv', 'wb', buffering=0))
        header_row = ["sid"]
        for cause in va_cause_list[0].rank_list.keys():
            header_row.append(cause)
        rank_writer.writerow(header_row)
        for va in va_cause_list:
            new_row = [va.sid]
            for cause in va.rank_list.keys():
                new_row.append(va.rank_list[cause])
            rank_writer.writerow(new_row)

        tariff_writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-scores.csv', 'wb', buffering=0))
        header_row = ["sid"]
        for cause in va_cause_list[0].cause_scores.keys():
            header_row.append(cause)
        tariff_writer.writerow(header_row)
        for va in va_cause_list:
            new_row = [va.sid]
            for cause in va.cause_scores.keys():
                new_row.append(va.cause_scores[cause])
            tariff_writer.writerow(new_row)

        writer.writerow(headers)
        for row in matrix:
            writer.writerow(row)

    def abort(self):
        self.want_abort = 1


def round5(value):
    return round(value / Decimal(.5)) * .5


def get_headers_and_matrix_from_file(file_name, mode='rU'):
    with open(file_name, mode) as f:
        reader = csv.reader(f)
        headers = next(reader)
        matrix = [_ for _ in reader]
    return headers, matrix
