import csv
import copy
from decimal import Decimal
import math
import os
import string

from smartva import config
from smartva import neonateuniformtrain
from smartva.freetext_vars import neonate_freetext
from smartva.hce_variables import neonate_hce
from smartva.short_form_remove import neonate_remove
from smartva.vacauses import neonatecauses
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier


# excel function..  =INDEX(B$1:D$1,MATCH(MIN(B2:D2),B2:D2,0))

# data structure we use to keep track of an manipulate data
class ScoredVA:
    def __init__(self, causescores, cause, sid, age, gender):
        self.causescores = causescores  # dict of {"cause1" : value, "cause2" :...}
        self.cause = cause  # int
        self.ranklist = {}
        self.sid = sid
        self.age = age
        self.gender = gender


class Tariff(object):
    AGE_GROUP = 'neonate'

    def __init__(self, input_file, output_dir, intermediate_dir, hce, freetext, country, shortform):
        """
        :type input_file: str
        :type output_dir: str
        :type intermediate_dir: str
        :type hce: bool
        :type freetext: bool
        :type malaria: bool
        :type country: str
        :type shortform: bool
        """
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.hce = hce
        self.freetext = freetext
        self.want_abort = 0
        self.iso3 = country
        self.intermediate_dir = intermediate_dir
        self.shortform = shortform

    def run(self):
        status_notifier.update({'progress': (12,)})

        reader = csv.reader(open(self.inputFilePath, 'rb'))
        writer = csv.writer(open(self.intermediate_dir + os.sep + 'neonate-tariff-results.csv', 'wb', buffering=0))

        status_logger.info('Neonate :: Calculating tariffs')

        tariff_file = os.path.join(config.basedir, 'tariffs-{:s}.csv'.format(self.AGE_GROUP))
        validated_file = os.path.join(config.basedir, 'validated-{:s}.csv'.format(self.AGE_GROUP))
        # If hce is False, use hce0, else use hce1
        undetermined_file = os.path.join(config.basedir, '{:s}_undetermined_weights-hce{:d}.csv'.format(self.AGE_GROUP, int(self.hce)))

        tariffreader = csv.reader(open(tariff_file, 'rU'))
        validatedreader = csv.reader(open(validated_file, 'rU'))
        undeterminedreader = csv.reader(open(undetermined_file, 'rU'))

        matrix = list()
        headers = list()

        tariffheaders = list()
        tariffmatrix = list()

        validatedheaders = list()
        validatedmatrix = list()

        undeterminedheaders = list()
        undeterminedmatrix = list()

        first = 1
        # read in new .csv for processing
        # we add the generated headers later this time
        for row in reader:
            if first == 1:
                for col in row:
                    headers.append(col)
                first = 0

            else:
                matrix.append(row)

        first = 1
        # read in new tariffs.csv for processing
        # we add the generated headers later this time
        for row in tariffreader:
            if first == 1:
                for col in row:
                    tariffheaders.append(col)
                first = 0

            else:
                tariffmatrix.append(row)

        first = 1
        # read in new validated .csv for processing
        # we add the generated headers later this time
        for row in validatedreader:
            if first == 1:
                for col in row:
                    validatedheaders.append(col)
                first = 0

            else:
                validatedmatrix.append(row)

        if len(matrix) == 0:
            # no entries, just return
            return

        first = 1
        # read in new undetermined .csv for processing
        for row in undeterminedreader:
            if first == 1:
                for col in row:
                    undeterminedheaders.append(col)
                first = 0

            else:
                undeterminedmatrix.append(row)

        if not self.hce:
            # remove all hce variables
            headers_copy = copy.deepcopy(headers)
            for col in headers_copy:
                if col in neonate_hce:
                    index = headers.index(col)
                    for row in matrix:
                        del row[index]
                    headers.remove(col)

            tariffheaders_copy = copy.deepcopy(tariffheaders)
            for col in tariffheaders_copy:
                if col in neonate_hce:
                    index = tariffheaders.index(col)
                    for row in tariffmatrix:
                        del row[index]
                    tariffheaders.remove(col)

            validatedheaders_copy = copy.deepcopy(validatedheaders)
            for col in validatedheaders_copy:
                if col in neonate_hce:
                    index = validatedheaders.index(col)
                    for row in validatedmatrix:
                        del row[index]
                    validatedheaders.remove(col)

        if not self.freetext and self.hce:
            # only need to do this if 'hce' is on and freetext is off, otherwise hce removes all freetext
            headers_copy = copy.deepcopy(headers)
            for col in headers_copy:
                if col in neonate_freetext:
                    index = headers.index(col)
                    for row in matrix:
                        del row[index]
                    headers.remove(col)

            tariffheaders_copy = copy.deepcopy(tariffheaders)
            for col in tariffheaders_copy:
                if col in neonate_freetext:
                    index = tariffheaders.index(col)
                    for row in tariffmatrix:
                        del row[index]
                    tariffheaders.remove(col)

            validatedheaders_copy = copy.deepcopy(validatedheaders)
            for col in validatedheaders_copy:
                if col in neonate_freetext:
                    index = validatedheaders.index(col)
                    for row in validatedmatrix:
                        del row[index]
                    validatedheaders.remove(col)

        if self.shortform:
            for d in neonate_remove:
                try:
                    index = headers.index(d)
                    # headers.remove(d)
                    for row in matrix:
                        row[index] = 0
                    # del row[index]

                    tariffindex = tariffheaders.index(d)
                    # tariffheaders.remove(d)
                    for row in tariffmatrix:
                        # del row[tariffindex]
                        row[tariffindex] = 0

                    validatedindex = validatedheaders.index(d)
                    # validatedheaders.remove(d)
                    for row in validatedmatrix:
                        # del row[validatedindex]
                        row[validatedindex] = 0
                except ValueError:
                    pass  # if the header doesn't exit, it was probably removed by hce

        # list of cause1: s1, s2, s50, ... top 40 svars per cause        
        cause40s = {}
        # for each cause, create a list with the top 40 's' variables     
        for i, row in enumerate(tariffmatrix):
            cause = row[0]
            # make a dictionary mapping 's' variables to values
            sdict = {}
            for j, col in enumerate(row):
                if j == 0:
                    continue  # noop, skip the first column
                # save absval, relval
                sdict[tariffheaders[j]] = math.fabs(float(row[j]))
            # sort the list based on the values of the svars                
            sorteddict = sorted(sdict.items(), key=lambda t: t[1], reverse=True)

            slist = []
            for val in sorteddict[:40]:
                slist.append(val[0])
            cause40s[cause] = slist

        # creates a list of causes/scores for each va.
        # va1 :: cause1/score, cause2/score...casue46/score
        # va2 :: cause1/score, cause2/score...
        # ...
        vacauselist = []
        for i, row in enumerate(matrix):
            causedict = {}
            for causenum in range(1, 7):
                cause = "cause" + str(causenum)
                slist = cause40s[cause]
                # for each svar, if it's 1, find the number in the tariff matrix and add it to the total
                causeval = 0.0
                for svar in slist:
                    index = headers.index(svar)
                    if row[index] == str(1):
                        tariffindex = tariffheaders.index(svar)
                        # row is causenum - 1 since causenum starts at 1 and index starts at 0
                        tariff = self.round5(Decimal(tariffmatrix[causenum - 1][tariffindex]))
                        causeval = causeval + float(tariff)
                causedict[cause] = causeval
            sid = row[headers.index('sid')]
            va = ScoredVA(causedict, row[validatedheaders.index('va34')], sid, row[headers.index('real_age')],
                          row[headers.index('real_gender')])
            vacauselist.append(va)

        status_logger.debug('Neonate :: Calculating scores for validated dataset.')
        # creates a list of causes/scores for each VALIDATED va.
        # va1 :: cause1/score, cause2/score...casue46/score
        # ... 

        vavalidatedcauselist = []
        max_cause = 6

        total = len(validatedmatrix) * max_cause
        div = min(10 ** len(str(abs(total))), 100)
        status_notifier.update({'sub_progress': (0, total)})

        for i, row in enumerate(validatedmatrix):
            causedict = {}
            for causenum in range(1, max_cause + 1):
                if self.want_abort == 1:
                    return
                cnt = (i * max_cause) + causenum
                if cnt % max((total / div), 1) == 0:
                    status_logger.debug('Neonate :: Processing %s of %s' % (cnt, total))
                    status_notifier.update({'sub_progress': (cnt,)})
                cause = "cause" + str(causenum)
                slist = cause40s[cause]
                causeval = 0.0
                for svar in slist:
                    index = validatedheaders.index(svar)
                    if row[index] == str(1):
                        tariffindex = tariffheaders.index(svar)
                        # in tariffmatrix, cause1 == row 0, so -1 from causenum
                        tariff = self.round5(Decimal(tariffmatrix[causenum - 1][tariffindex]))
                        causeval = causeval + float(tariff)
                causedict[cause] = causeval
            sid = row[validatedheaders.index('sid')]
            va = ScoredVA(causedict, row[validatedheaders.index('va34')], sid, 0, 0)
            vavalidatedcauselist.append(va)

        status_logger.debug('Neonate :: Processing %s of %s' % (total, total))
        status_notifier.update({'sub_progress': (0, 1)})

        status_logger.debug('Neonate :: Creating uniform training set')
        # creates the new "uniform train" data set from the validation data
        # find the cause of death with the most deaths, and use that number
        # as the sample size
        # also track row indexes of each cause

        # va34 is the validated cause of death
        index = validatedheaders.index('va34')
        # count is a dictionary of {cause : count}
        causecount = {}
        # causeindexes is a list of indexes for a particular cause {cause : [1, 2, 3...], cause2:...}
        causeindexes = {}
        for i, row in enumerate(validatedmatrix):
            cause = row[index]
            if cause not in causecount.keys():
                # if the key doesn't exist, create it
                causecount[cause] = 1
                causeindexes[cause] = [i]
            else:
                # if the key does exist, increment it by 1
                causecount[cause] = causecount[cause] + 1
                causeindexes[cause].append(i)

        # now sort by size
        sortedcausecount = sorted(causecount.items(), key=lambda t: t[1], reverse=True)
        # sample size is the first (0th) element of the list, and the second (1th) item of that element
        samplesize = sortedcausecount[0][1]

        # create new uniform training set using the frequencies file
        uniformtrain = {}
        for cause in range(1, 7):
            uniformtrain[str(cause)] = []
            # indexes of all VAs of a certain cause
            for causeindex in causeindexes[str(cause)]:
                va = validatedmatrix[causeindex]
                sid = va[validatedheaders.index('sid')]
                count = int(neonateuniformtrain.frequencies[sid])
                for i in range(0, count):
                    uniformtrain[str(cause)].append(vavalidatedcauselist[causeindex])

        # create a list of ALL the VAs in our uniform set
        uniformlist = []
        for key in uniformtrain.keys():
            # vas this should be 600ish long
            vas = uniformtrain[key]
            for va in vas:
                uniformlist.append(va)

        status_logger.debug('Neonate :: Generating cause rankings.')

        total = len(vacauselist) * max_cause
        div = min(10 ** len(str(abs(total))), 100)
        status_notifier.update({'sub_progress': (0, total)})

        for i, va in enumerate(vacauselist):
            sortedtariffs = []
            ranklist = {}
            for causenum in range(1, max_cause + 1):
                if self.want_abort == 1:
                    return
                cnt = (i * max_cause) + causenum
                if cnt % max((total / div), 1) == 0:
                    status_logger.debug('Neonate :: Processing %s of %s' % (cnt, total))
                    status_notifier.update({'sub_progress': (cnt,)})
                cause = "cause" + str(causenum)
                # get the tariff score for this cause for this external VA
                deathscore = va.causescores[cause]
                # make a list of tariffs of ALL validated VAs for this cause
                tariffs = []
                for validatedva in uniformlist:
                    tariffs.append(validatedva.causescores[cause])

                # sort them and calculate absolute value of tariff-deathscore
                sortedtariffs = sorted(tariffs, reverse=True)
                for idx, val in enumerate(sortedtariffs):
                    sortedtariffs[idx] = math.fabs(val - deathscore)

                minlist = []
                minval = 10000

                # loop through all the new scores, find the minimum value, store that index
                # if there are multiple minimum values that are the same, take the mean of the indexes
                for index, val in enumerate(sortedtariffs):
                    if val < minval:
                        minval = val
                        minlist = [index]
                    elif val == minval:
                        minlist.append(index)

                index = sum(minlist) / float(len(minlist))
                # add 1 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                ranklist[cause] = index + 1
            va.ranklist = ranklist

        status_logger.debug('Neonate :: Processing %s of %s' % (total, total))
        status_notifier.update({'sub_progress': (0, 1)})

        rankwriter = csv.writer(open(self.intermediate_dir + os.sep + 'neonate-external-ranks.csv', 'wb', buffering=0))
        headerrow = []
        headerrow.append("sid")
        for cause in vacauselist[0].ranklist.keys():
            headerrow.append(cause)
        rankwriter.writerow(headerrow)
        for va in vacauselist:
            newrow = []
            newrow.append(va.sid)
            for cause in va.ranklist.keys():
                newrow.append(va.ranklist[cause])
            rankwriter.writerow(newrow)

        for i in range(1, 7):
            cause = "cause" + str(i)
            causelist = []
            for va in uniformlist:
                causelist.append([va.sid, va.causescores[cause], va])
            sortedcauselist = sorted(causelist, key=lambda t: t[1], reverse=True)
            for j, item in enumerate(sortedcauselist):
                item[2].ranklist[cause] = j

        status_logger.debug('Neonate :: Generating cutoffs')

        cutoffs = []
        for i in range(1, 7):
            causelist = []
            for va in uniformlist:
                causelist.append([va.cause, va.causescores["cause" + str(i)], va.sid, va])
            causelist.sort(key=lambda t: t[2])
            causelist.sort(key=lambda t: t[1], reverse=True)
            sortedlist = causelist

            locallist = []
            for j, va in enumerate(sortedlist):
                if va[0] == str(i):
                    # j is the "rank"
                    # we add one because python is 0 indexed and stata is 1 indexed, so this will give us the
                    # same numbers as the original stata tool
                    locallist.append(j + 1)
            # make it an int, don't round
            index = int(len(locallist) * .91)
            cutoffs.append(locallist[index])

        f = open(self.intermediate_dir + os.sep + 'neonate-cutoffs.txt', 'w')
        for i, cutoff in enumerate(cutoffs):
            f.write(str(i + 1) + " : " + str(cutoff) + "\n")
        f.close()

        # lowest rank is actually the biggest number
        lowest = 0
        # find the lowest rank and then add 1 to it
        for va in vacauselist:
            for cause in va.ranklist.keys():
                if float(va.ranklist[cause]) > 0 and float(va.ranklist[cause]) > lowest:
                    lowest = float(va.ranklist[cause])
        lowest = lowest + 1

        # if a VA has a tariff score less than 0 for a certain cause,
        # replace the rank for that cause with the lowest possible rank
        for va in vacauselist:
            for cause in va.causescores.keys():
                if float(va.causescores[cause]) < 0:
                    va.ranklist[cause] = lowest

        for va in vacauselist:
            for i in range(1, 7):
                if float(va.ranklist["cause" + str(i)]) > float(cutoffs[i - 1]):
                    va.ranklist["cause" + str(i)] = lowest
                elif float(va.ranklist["cause" + str(i)]) > float(len(uniformlist) * .35):
                    va.ranklist["cause" + str(i)] = lowest
                elif float(va.causescores["cause" + str(i)]) < 1.0:
                    va.ranklist["cause" + str(i)] = lowest

        causecounts = {}
        rankwriter = csv.writer(open(self.output_dir + os.sep + 'neonate-predictions.csv', 'wb', buffering=0))
        rankwriter.writerow(['sid', 'cause', 'cause34', 'age', 'sex'])

        # Insert stillborn (never cried, moved, or breathed) into va
        # c1_15 in the pre-symptom file, AKA s20 in the symptom file, AKA child_1_15 in the original input.
        indx = headers.index('s20')
        S20 = zip(*matrix)[indx]  # Transpose
        for s20, va in zip(S20, vacauselist):
            va.s20 = s20

        for va in vacauselist:
            causescore = lowest
            realcause = 'Undetermined'
            cause34 = ''
            causenum = ''
            multiple = {}
            for cause in va.ranklist:
                if float(va.ranklist[cause]) < causescore:
                    causescore = float(va.ranklist[cause])
                    realcause = cause
                    cause34 = string.strip(cause, 'cause')
                    causenum = cause34
                    multiple[va.sid] = [cause]
                elif causescore == float(va.ranklist[cause]) and causescore != lowest:
                    multiple[va.sid].append(cause)

            # Notify user if multiple causes have been determined.
            for sid_key, causes in multiple.items():
                if len(causes) > 1:
                    warning_logger.info(
                        '{group:s} :: VA {sid:s} had multiple matching results {causes}, using {causes[0]}'.format(
                            group=self.AGE_GROUP.capitalize(), sid=sid_key, causes=causes))

            # Check to see if there is a special stillbirth value
            if va.s20 == '1':
                # set cause34 to stillbirth
                cause34 = '6'
                causenum = '6'

            # replace number with word for cause:
            if cause34 == '':
                cause34 = 'Undetermined'
                if self.iso3 is None:
                    if cause34 in causecounts.keys():
                        causecounts[cause34] = causecounts[cause34] + 1.0
                    else:
                        causecounts[cause34] = 1.0
                else:
                    # for undetermined, look up the values for each cause using keys (age, sex, country) and
                    # add them to the 'count' for that cause
                    for uRow in undeterminedmatrix:
                        ageValidated = False
                        if int(uRow[undeterminedheaders.index('age')]) == 0 and float(va.age) >= 0 and float(va.age) < 7:
                            ageValidated = True
                        elif int(uRow[undeterminedheaders.index('age')]) == 7 and float(va.age) >= 7 and float(va.age) < 28:
                            ageValidated = True
                        if uRow[undeterminedheaders.index('sex')] == va.gender and ageValidated is True and uRow[undeterminedheaders.index('iso3')] == self.iso3:
                            # print "gender = %s and age = %s and country = %s" % (va.gender, va.age, self.iso3)
                            # get the value and add it
                            if uRow[undeterminedheaders.index('gs_text34')] in causecounts.keys():
                                # print " adding %s" % float(uRow[undeterminedheaders.index('GBD_weight')])
                                causecounts[uRow[undeterminedheaders.index('gs_text34')]] = causecounts[uRow[undeterminedheaders.index('gs_text34')]] + float(uRow[undeterminedheaders.index('weight')])
                            else:
                                # print " started at %s" % float(uRow[undeterminedheaders.index('GBD_weight')])
                                causecounts[uRow[undeterminedheaders.index('gs_text34')]] = float(uRow[undeterminedheaders.index('weight')])
            else:
                cause34 = neonatecauses[cause34]
                # print "found cause: %s" % cause34
                if cause34 in causecounts.keys():
                    causecounts[cause34] = causecounts[cause34] + 1.0
                    # print "adding 1"
                else:
                    causecounts[cause34] = 1.0
                    # print "starting at 1"
            # print "neonate va was %s" % cause34
            rankwriter.writerow([va.sid, causenum, cause34, va.age, va.gender])

        csmfwriter = csv.writer(open(self.output_dir + os.sep + 'neonate-csmf.csv', 'wb', buffering=0))
        csmfheaders = ["cause", "CSMF"]
        csmfwriter.writerow(csmfheaders)
        for causekey in causecounts.keys():
            # FIXME: original approach to calculating CSMFs did not sum to
            # 100%; perhaps this is due to deaths where the age is
            # missing, which is handled in block of a complex conditionals
            # above.
            # percent = float(causecounts[causekey])/float(len(matrix))
            percent = float(causecounts[causekey]) / float(sum(causecounts.values()))

            csmfwriter.writerow([causekey, percent])

        # TODO: enable this test, that confirm that csmf sums to 100%
        # (after fixing issue flagged above)
        # assert int(sum(causecounts.values())) == len(matrix), \
        #             'CSMF must sum to one'

        rankwriter = csv.writer(open(self.intermediate_dir + os.sep + 'neonate-tariff-ranks.csv', 'wb', buffering=0))
        headerrow = []
        headerrow.append("sid")
        for cause in vacauselist[0].ranklist.keys():
            headerrow.append(cause)
        rankwriter.writerow(headerrow)
        for va in vacauselist:
            newrow = []
            newrow.append(va.sid)
            for cause in va.ranklist.keys():
                newrow.append(va.ranklist[cause])
            rankwriter.writerow(newrow)

        tariffwriter = csv.writer(open(self.intermediate_dir + os.sep + 'neonate-tariff-scores.csv', 'wb', buffering=0))
        headerrow = []
        headerrow.append("sid")
        for cause in vacauselist[0].causescores.keys():
            headerrow.append(cause)
        tariffwriter.writerow(headerrow)
        for va in vacauselist:
            newrow = []
            newrow.append(va.sid)
            for cause in va.causescores.keys():
                newrow.append(va.causescores[cause])
            tariffwriter.writerow(newrow)

        # end
        writer.writerow(headers)
        for row in matrix:
            writer.writerow(row)

        return 1

    def round5(self, value):
        return round(value / Decimal(.5)) * .5

    def abort(self):
        self.want_abort = 1
