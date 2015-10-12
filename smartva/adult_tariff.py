import csv
import copy
from decimal import Decimal
import math
import os

from smartva import adultuniformtrain
from smartva import config
from smartva.freetext_vars import ADULT_FREE_TEXT
from smartva.hce_variables import adult_hce
from smartva.loggers import status_logger, warning_logger
from smartva.short_form_remove import adult_remove
from smartva.vacauses import adultcauses
from smartva.utils import status_notifier


# data structure we use to keep track of an manipulate data
class ScoredVA(object):
    def __init__(self, cause_scores, cause, sid, age, gender):
        self.cause_scores = cause_scores  # dict of {"cause1" : value, "cause2" :...}
        self.cause = cause  # int
        self.rank_list = {}
        self.sid = sid
        self.age = age
        self.gender = gender


class Tariff(object):
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
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.intermediate_dir = intermediate_dir
        self.hce = hce
        self.free_text = free_text
        self.malaria = malaria
        self.iso3 = country
        self.short_form = short_form

        self.want_abort = False

    def run(self):
        status_logger.info('Adult :: Processing Adult tariffs')
        status_notifier.update({'progress': (4,)})

        headers, matrix = get_headers_and_matrix_from_file(self.input_file_path, 'rb')

        tariff_headers, tariff_matrix = get_headers_and_matrix_from_file(
            os.path.join(config.basedir, 'tariffs-{:s}.csv'.format(self.AGE_GROUP)))

        validated_headers, validated_matrix = get_headers_and_matrix_from_file(
            os.path.join(config.basedir, 'validated-{:s}.csv'.format(self.AGE_GROUP)))

        undetermined_headers, undetermined_matrix = get_headers_and_matrix_from_file(
            os.path.join(config.basedir, '{:s}_undetermined_weights-hce{:d}.csv'.format(self.AGE_GROUP, int(self.hce))))

        writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-results.csv', 'wb', buffering=0))

        if not self.hce:
            # remove all hce variables
            headers_copy = copy.deepcopy(headers)
            for col in headers_copy:
                if col in adult_hce:
                    index = headers.index(col)
                    for row in matrix:
                        del row[index]
                    headers.remove(col)

            tariff_headers_copy = copy.deepcopy(tariff_headers)
            for col in tariff_headers_copy:
                if col in adult_hce:
                    index = tariff_headers.index(col)
                    for row in tariff_matrix:
                        del row[index]
                    tariff_headers.remove(col)

            validated_headers_copy = copy.deepcopy(validated_headers)
            for col in validated_headers_copy:
                if col in adult_hce:
                    index = validated_headers.index(col)
                    for row in validated_matrix:
                        del row[index]
                    validated_headers.remove(col)

        if not self.free_text and self.hce:
            # only need to do this if 'hce' is on and free text is off, otherwise hce removes all free text
            headers_copy = copy.deepcopy(headers)
            for col in headers_copy:
                if col in ADULT_FREE_TEXT:
                    index = headers.index(col)
                    for row in matrix:
                        del row[index]
                    headers.remove(col)

            tariff_headers_copy = copy.deepcopy(tariff_headers)
            for col in tariff_headers_copy:
                if col in ADULT_FREE_TEXT:
                    index = tariff_headers.index(col)
                    for row in tariff_matrix:
                        del row[index]
                    tariff_headers.remove(col)

            validated_headers_copy = copy.deepcopy(validated_headers)
            for col in validated_headers_copy:
                if col in ADULT_FREE_TEXT:
                    index = validated_headers.index(col)
                    for row in validated_matrix:
                        del row[index]
                    validated_headers.remove(col)

        if self.short_form:
            for d in adult_remove:
                try:
                    index = headers.index(d)
                    # headers.remove(d)
                    for row in matrix:
                        row[index] = 0
                        # del row[index]

                    tariff_index = tariff_headers.index(d)
                    # tariff_headers.remove(d)
                    for row in tariff_matrix:
                        # del row[tariff_index]
                        row[tariff_index] = 0

                    validated_index = validated_headers.index(d)
                    # validated_headers.remove(d)
                    for row in validated_matrix:
                        # del row[validated_index]
                        row[validated_index] = 0
                except ValueError:
                    pass  # if the header doesn't exit, it was probably removed by hce

        # list of cause1: s1, s2, s50, ... top 40 s_vars per cause
        cause40s = {}
        # for each cause, create a list with the top 40 's' variables     
        for i, row in enumerate(tariff_matrix):
            cause = row[0]
            # make a dictionary mapping 's' variables to values
            s_dict = {}
            for j, col in enumerate(row):
                if j == 0:
                    continue  # noop, skip the first column
                # save absval, relval
                s_dict[tariff_headers[j]] = math.fabs(float(row[j]))
            # sort the list based on the values of the s_vars
            sorted_dict = sorted(s_dict.items(), key=lambda t: t[1], reverse=True)

            s_list = []
            for val in sorted_dict[:40]:
                s_list.append(val[0])
            cause40s[cause] = s_list
            # print "cause: %s :: %s" % (cause, s_list)

        #        for cause in cause40s.keys():
        #            asdf = cause40s[cause]
        #            asdf.sort()
        #            print "cause: %s :: %s" % (cause, asdf)

        # creates a list of causes/scores for each va.
        # va1 :: cause1/score, cause2/score...cause46/score
        # va2 :: cause1/score, cause2/score...
        # ...
        va_cause_list = []
        for i, row in enumerate(matrix):
            cause_dict = {}
            for cause_num in range(1, 47):
                cause = "cause" + str(cause_num)
                s_list = cause40s[cause]
                # for each s_var, if it's 1, find the number in the tariff matrix and add it to the total
                cause_val = 0.0
                for s_var in s_list:
                    index = headers.index(s_var)
                    if row[index] == str(1):
                        tariff_index = tariff_headers.index(s_var)
                        # row is cause_num - 1 since cause_num starts at 1 and index starts at 0
                        tariff = self.round5(Decimal(tariff_matrix[cause_num - 1][tariff_index]))
                        cause_val += float(tariff)
                cause_dict[cause] = cause_val
            sid = row[headers.index('sid')]
            va = ScoredVA(cause_dict, row[validated_headers.index('va46')], sid, row[headers.index('real_age')],
                          row[headers.index('real_gender')])
            va_cause_list.append(va)

        status_logger.debug('Adult :: Calculating scores for validated dataset.')

        # creates a list of causes/scores for each VALIDATED va.
        # va1 :: cause1/score, cause2/score...cause46/score
        # ... 

        va_validated_cause_list = []
        max_cause = 46

        total = len(validated_matrix) * max_cause
        div = min(10 ** len(str(abs(total))), 100)
        status_notifier.update({'sub_progress': (0, total)})

        for i, row in enumerate(validated_matrix):
            cause_dict = {}
            for cause_num in range(1, max_cause + 1):
                if self.want_abort == 1:
                    return
                cnt = (i * max_cause) + cause_num
                if cnt % max((total / div), 1) == 0:
                    status_logger.debug('Adult :: Processing %s of %s' % (cnt, total))
                    status_notifier.update({'sub_progress': (cnt,)})
                cause = "cause" + str(cause_num)
                s_list = cause40s[cause]
                cause_val = 0.0
                for s_var in s_list:
                    index = validated_headers.index(s_var)
                    if row[index] == str(1):
                        tariff_index = tariff_headers.index(s_var)
                        # in tariff_matrix, cause1 == row 0, so -1 from cause_num
                        tariff = self.round5(Decimal(tariff_matrix[cause_num - 1][tariff_index]))
                        cause_val += float(tariff)
                cause_dict[cause] = cause_val
            sid = row[validated_headers.index('sid')]
            va = ScoredVA(cause_dict, row[validated_headers.index('va46')], sid, 0, 0)
            va_validated_cause_list.append(va)

        status_logger.debug('Adult :: Processing %s of %s' % (total, total))
        status_notifier.update({'sub_progress': None})

        status_logger.debug('Adult :: Creating uniform training set')
        # creates the new "uniform train" data set from the validation data
        # find the cause of death with the most deaths, and use that number
        # as the sample size
        # also track row indexes of each cause

        # va46 is the validated cause of death
        index = validated_headers.index('va46')
        # count is a dictionary of {cause : count}
        cause_count = {}
        # cause_indexes is a list of indexes for a particular cause {cause : [1, 2, 3...], cause2:...}
        cause_indexes = {}
        for i, row in enumerate(validated_matrix):
            cause = row[index]
            if cause not in cause_count.keys():
                # if the key doesn't exist, create it
                cause_count[cause] = 1
                cause_indexes[cause] = [i]
            else:
                # if the key does exist, increment it by 1
                cause_count[cause] += 1
                cause_indexes[cause].append(i)

        # now sort by size
        sorted_cause_count = sorted(cause_count.items(), key=lambda t: t[1], reverse=True)
        # sample size is the first (0th) element of the list, and the second (1th) item of that element
        sample_size = sorted_cause_count[0][1]

        # create new uniform training set using the frequencies file
        uniform_train = {}
        for cause in range(1, 47):
            uniform_train[str(cause)] = []
            # indexes of all VAs of a certain cause
            for cause_index in cause_indexes[str(cause)]:
                va = validated_matrix[cause_index]
                sid = va[validated_headers.index('sid')]
                count = int(adultuniformtrain.frequencies[sid])
                for i in range(0, count):
                    uniform_train[str(cause)].append(va_validated_cause_list[cause_index])

        # create a list of ALL the VAs in our uniform set
        uniform_list = []
        for key in uniform_train.keys():
            # vas this should be 600ish long
            vas = uniform_train[key]
            for va in vas:
                uniform_list.append(va)

        status_logger.debug('Adult :: Generating cause rankings.')

        total = len(va_cause_list) * max_cause
        div = min(10 ** len(str(abs(total))), 100)
        status_notifier.update({'sub_progress': (0, total)})

        for i, va in enumerate(va_cause_list):
            sorted_tariffs = []
            rank_list = {}
            for cause_num in range(1, max_cause + 1):
                if self.want_abort == 1:
                    return
                cnt = (i * max_cause) + cause_num
                if cnt % max((total / div), 1) == 0:
                    status_logger.debug('Adult :: Processing %s of %s' % (cnt, total))
                    status_notifier.update({'sub_progress': (cnt,)})
                cause = "cause" + str(cause_num)
                # get the tariff score for this cause for this external VA
                death_score = va.cause_scores[cause]
                # make a list of tariffs of ALL validated VAs for this cause
                tariffs = []
                for validated_va in uniform_list:
                    tariffs.append(validated_va.cause_scores[cause])

                # sort them and calculate absolute value of tariff-death_score
                sorted_tariffs = sorted(tariffs, reverse=True)

                for idx, val in enumerate(sorted_tariffs):
                    sorted_tariffs[idx] = math.fabs(val - death_score)

                min_list = []
                min_val = None

                # loop through all the new scores, find the minimum value, store that index
                # if there are multiple minimum values that are the same, take the mean of the indexes
                for index, val in enumerate(sorted_tariffs):
                    if val < min_val or min_val is None:
                        min_val = val
                        min_list = [index]
                    elif val == min_val:
                        min_list.append(index)

                index = sum(min_list) / float(len(min_list))
                # add 1 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                rank_list[cause] = index + 1
            va.rank_list = rank_list

        status_logger.debug('Adult :: Processing %s of %s' % (total, total))
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
                        if uRow[undetermined_headers.index('sex')] == va.gender and (
                            (int(va.age) <= int(uRow[undetermined_headers.index('age')]) < int(va.age) + 5) or (
                                int(va.age) > 80 and int(uRow[undetermined_headers.index('age')]) == 80)) and uRow[
                            undetermined_headers.index('iso3')] == self.iso3:
                            # get the value and add it
                            if uRow[undetermined_headers.index('gs_text34')] in cause_counts.keys():
                                cause_counts[uRow[undetermined_headers.index('gs_text34')]] += float(
                                    uRow[undetermined_headers.index('weight')])
                            else:
                                cause_counts[uRow[undetermined_headers.index('gs_text34')]] = float(
                                    uRow[undetermined_headers.index('weight')])
            else:
                cause34 = adultcauses[cause34]
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

    @staticmethod
    def round5(value):
        return round(value / Decimal(.5)) * .5

    def abort(self):
        self.want_abort = 1


def get_headers_and_matrix_from_file(file_name, mode='rU'):
    with open(file_name, 'rU') as f:
        reader = csv.reader(f)
        headers = next(reader)
        matrix = [_ for _ in reader]
    return headers, matrix
