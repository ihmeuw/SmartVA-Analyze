#!/opt/virtualenvs/ihme-va/bin/pythonw

import csv
import copy
import math
from decimal import Decimal
import os
import platform
import sys

import wx

import workerthread
from freetext_vars import adult_freetext
from hce_variables import adult_hce
from vacauses import adultcauses
import adultuniformtrain
import config

from short_form_remove import adult_remove



# data structure we use to keep track of an manipulate data
class ScoredVA:
    def __init__(self, causescores, cause, sid, age, gender):
        self.causescores = causescores #dict of {"cause1" : value, "cause2" :...}
        self.cause = cause #int
        self.ranklist = {}
        self.sid = sid
        self.age = age
        self.gender = gender
            

class Tariff():
    def __init__(self, notify_window, input_file, output_dir, intermediate_dir, hce, freetext, malaria, country, shortform):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.hce = hce
        self.freetext = freetext
        self.want_abort = 0
        self.malaria = malaria
        self.iso3 = country
        self.intermediate_dir = intermediate_dir
        self.shortform = shortform
        

    def run(self):
        reader = csv.reader(open( self.inputFilePath, 'rb'))
        writer = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-results.csv', 'wb', buffering=0))
        
        updatestr = "Adult :: Processing Adult tariffs\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        
        
        tarifffile = 'tariffs-adult.csv'
        validatedfile = 'validated-adult.csv'
        undeterminedfile = 'adult_undetermined_weights'
        if self.hce is None:
            undeterminedfile = undeterminedfile + "-hce0.csv"
        else:
            undeterminedfile = undeterminedfile + "-hce1.csv"
#        if (platform.system() == "Windows" or platform.system() == "Darwin") and getattr(sys, 'frozen', None):
        if getattr(sys, 'frozen', None) or platform.system() == "Windows":
            tarifffile = os.path.join(config.basedir, 'tariffs-adult.csv')
            validatedfile =  os.path.join(config.basedir, 'validated-adult.csv')
            undeterminedfile = os.path.join(config.basedir,  undeterminedfile)
        
        tariffreader = csv.reader(open(tarifffile, 'rU'))
        validatedreader = csv.reader(open(validatedfile, 'rU'))
        undeterminedreader = csv.reader(open(undeterminedfile, 'rU'))
        
        
        
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
                
        #print tariffmatrix
                
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
            #no entries, just return
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
                
        
        if self.hce is None:
            # remove all hce variables
            headers_copy = copy.deepcopy(headers)
            for col in headers_copy:
                if col in adult_hce:
                    index = headers.index(col)
                    for row in matrix:
                        del row[index]
                    headers.remove(col)
                
            tariffheaders_copy = copy.deepcopy(tariffheaders)
            for col in tariffheaders_copy:
                if col in adult_hce:
                    index = tariffheaders.index(col)
                    for row in tariffmatrix:
                        del row[index]
                    tariffheaders.remove(col)
            
            validatedheaders_copy = copy.deepcopy(validatedheaders)
            for col in headers_copy:
                if col in adult_hce:
                    index = validatedheaders.index(col)
                    for row in validatedmatrix:
                        del row[index]
                    validatedheaders.remove(col)
        
        if self.freetext is None and self.hce is 'hce':
            # only need to do this if 'hce' is on and freetext is off, otherwise hce removes all freetext
            headers_copy = copy.deepcopy(headers)
            for col in headers_copy:
                if col in adult_freetext:
                    index = headers.index(col)
                    for row in matrix:
                        del row[index]
                    headers.remove(col)
                
            tariffheaders_copy = copy.deepcopy(tariffheaders)
            for col in tariffheaders_copy:
                if col in adult_freetext:
                    index = tariffheaders.index(col)
                    for row in tariffmatrix:
                        del row[index]
                    tariffheaders.remove(col)
            
            validatedheaders_copy = copy.deepcopy(validatedheaders)
            for col in validatedheaders_copy:
                if col in adult_freetext:
                    index = validatedheaders.index(col)
                    for row in validatedmatrix:
                        del row[index]
                    validatedheaders.remove(col)

        if self.shortform:
            for d in adult_remove:
                try:
                    index = headers.index(d)
                    #headers.remove(d)
                    for row in matrix:
                        row[index] = 0
                        #del row[index]

                    tariffindex = tariffheaders.index(d)
                    #tariffheaders.remove(d)
                    for row in tariffmatrix:
                        #del row[tariffindex]
                        row[tariffindex] = 0

                    validatedindex = validatedheaders.index(d)
                    #validatedheaders.remove(d)
                    for row in validatedmatrix:
                        #del row[validatedindex]
                        row[validatedindex] = 0
                except ValueError:
                    a = 1 #noop.  if the header doesn't exit, it was probably removed by hce
                    



        # list of cause1: s1, s2, s50, ... top 40 svars per cause
        cause40s = {}
        # for each cause, create a list with the top 40 's' variables     
        for i, row in enumerate(tariffmatrix):
            cause = row[0]
            # make a dictionary mapping 's' variables to values
            sdict = {}
            for j, col in enumerate(row):
                if j == 0:
                    continue # noop, skip the first column
                # save absval, relval
                sdict[tariffheaders[j]] = math.fabs(float(row[j]))
            # sort the list based on the values of the svars                
            sorteddict = sorted(sdict.items(), key=lambda t: t[1], reverse=True)

            slist = []
            for val in sorteddict[:40]:
                slist.append(val[0])
            cause40s[cause] = slist
                    #print "cause: %s :: %s" % (cause, slist)
        
#        for cause in cause40s.keys():
#            asdf = cause40s[cause]
#            asdf.sort()
#            print "cause: %s :: %s" % (cause, asdf)

        # creates a list of causes/scores for each va.
        # va1 :: cause1/score, cause2/score...casue46/score
        # va2 :: cause1/score, cause2/score...
        #...
        vacauselist = []
        for i, row in enumerate(matrix):
            causedict = {}
            for causenum in range(1,47):
                cause = "cause" + str(causenum)
                slist = cause40s[cause]
                # for each svar, if it's 1, find the number in the tariff matrix and add it to the total
                causeval = 0.0
                for svar in slist:
                    index = headers.index(svar)
                    if row[index] == str(1):
                        tariffindex = tariffheaders.index(svar)
                        # row is causenum - 1 since causenum starts at 1 and index starts at 0
                        tariff = self.round5(Decimal(tariffmatrix[causenum-1][tariffindex]))
                        causeval = causeval + float(tariff)
                causedict[cause] = causeval
            sid = row[headers.index('sid')]
            va = ScoredVA(causedict, row[validatedheaders.index('va46')], sid, row[headers.index('real_age')], row[headers.index('real_gender')])
            vacauselist.append(va)
            
       
        updatestr = "Adult :: Calculating scores for validated dataset.  (This takes a few minutes)\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))    
        # creates a list of causes/scores for each VALIDATED va.
        # va1 :: cause1/score, cause2/score...casue46/score
        # ... 
                
        vavalidatedcauselist = []
        total = len(validatedmatrix) * 46
        cnt = 0
        for i, row in enumerate(validatedmatrix):
            causedict = {}
            for causenum in range(1,47):
                if (self.want_abort == 1):
                    return
                cnt = cnt + 1
                progress = "Adult :: Processing %s of %s" % (cnt, total)
                if (cnt % 1000 == 0):
                    wx.PostEvent(self._notify_window, workerthread.ResultEvent(progress))
                cause = "cause" + str(causenum)
                slist = cause40s[cause]
                causeval = 0.0
                for svar in slist:
                    index = validatedheaders.index(svar)
                    if row[index] == str(1):
                        tariffindex = tariffheaders.index(svar)
                        # in tariffmatrix, cause1 == row 0, so -1 from causenum
                        tariff = self.round5(Decimal(tariffmatrix[causenum-1][tariffindex]))
                        causeval = causeval + float(tariff)
                causedict[cause] = causeval
            sid = row[validatedheaders.index('sid')]
            va = ScoredVA(causedict, row[validatedheaders.index('va46')], sid, 0, 0)
            vavalidatedcauselist.append(va)
        progress = "Adult :: Processing %s of %s\n" % (total, total)
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(progress)) 
                    
        updatestr = "Adult :: Creating uniform training set\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))        
        # creates the new "uniform train" data set from the validation data
        # find the cause of death with the most deaths, and use that number
        # as the sample size
        # also track row indexes of each cause
        
        #va46 is the validated cause of death
        index = validatedheaders.index('va46')
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
        
        #create new uniform training set using the frequencies file
        uniformtrain = {}
        for cause in range(1, 47):
            uniformtrain[str(cause)] = []
            #indexes of all VAs of a certain cause
            for causeindex in causeindexes[str(cause)]:
                va = validatedmatrix[causeindex]
                sid = va[validatedheaders.index('sid')]
                count = int(adultuniformtrain.frequencies[sid])
                for i in range(0, count):
                    uniformtrain[str(cause)].append(vavalidatedcauselist[causeindex])

        # create a list of ALL the VAs in our uniform set
        uniformlist = []
        for key in uniformtrain.keys():
            # vas this should be 600ish long
            vas = uniformtrain[key]
            for va in vas:
                uniformlist.append(va)
        
        
        updatestr = "Adult :: Generating cause rankings. (This takes a few minutes)\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

        total = len(vacauselist) * 46
        cnt = 0
        for va in vacauselist:
            sortedtariffs = []
            ranklist = {}
            for i in range(1, 47):
                if (self.want_abort == 1):
                    return
                cnt = cnt + 1
                progress = "Adult :: Processing %s of %s" % (cnt, total)
                if (cnt % 10 == 0):
                    wx.PostEvent(self._notify_window, workerthread.ResultEvent(progress))
                cause = "cause" + str(i)
                # get the tariff score for this cause for this external VA
                deathscore = va.causescores[cause]
                # make a list of tariffs of ALL validated VAs for this cause
                tariffs = []
                for validatedva in uniformlist:
                    tariffs.append(validatedva.causescores[cause])

                # sort them and calculate absolute value of tariff-deathscore
                sortedtariffs = sorted(tariffs, reverse=True)

                for idx, val in enumerate(sortedtariffs):
                    sortedtariffs[idx] = math.fabs(val-deathscore)

                minlist = []
                minval = None
                
                # loop through all the new scores, find the minimum value, store that index
                # if there are multiple minimum values that are the same, take the mean of the indexes
                for index, val in enumerate(sortedtariffs):
                    if val < minval or minval is None:
                        minval = val
                        minlist = [index]
                    elif val == minval:
                        minlist.append(index)
                
                index = sum(minlist)/float(len(minlist))
                # add 1 because python is zero indexed, and stata is 1 indexed so we get the same
                # answer as the original stata tool
                ranklist[cause] = index+1
            va.ranklist = ranklist
        progress = "Adult :: Processing %s of %s\n" % (total, total)
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(progress)) 
            
        rankwriter = csv.writer(open(self.intermediate_dir + os.sep + 'adult-external-ranks.csv', 'wb', buffering=0))
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
                

            
        for i in range(1, 47):
            cause = "cause" + str(i)
            causelist = []
            for va in uniformlist:
                causelist.append([va.sid, va.causescores[cause], va])
            sortedcauselist = sorted(causelist, key=lambda t:t[1], reverse=True)
            # now have a sorted list of sid, causescore for a specific cause
            for j, item in enumerate(sortedcauselist):
                item[2].ranklist[cause] = j
                
        updatestr = "Adult :: Generating cutoffs\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        
        cutoffs = []
        for i in range(1, 47):
            causelist = []
            for va in uniformlist:
                causelist.append([va.cause, va.causescores["cause" + str(i)], va.sid, va])
                
            causelist.sort(key=lambda t: t[2])
            causelist.sort(key=lambda t: t[1], reverse=True)
            sortedlist = causelist
            
            locallist = []
            for j, va in enumerate(sortedlist):
                if va[0] == str(i):
                    # we add one because python is 0 indexed and stata is 1 indexed, so this will give us the same numbers
                    # as the original stata tool
                    locallist.append(j+1)

            #make it an int, don't round
            index = int(len(locallist) * .89)  
            cutoffs.append(locallist[index])
        
                        
        f = open(self.intermediate_dir + os.sep + 'adult-cutoffs.txt','w')
        for i, cutoff in enumerate(cutoffs):
            f.write(str(i+1) + " : " + str(cutoff) + "\n")
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
	
	    
        for i, row in enumerate(matrix):
            age = int(row[headers.index('real_age')])
            sex = int(row[headers.index('real_gender')])
                    
            # only females ages 15-49 can have anaemia, haemorrhage, hypertensive disease, other pregnancy-related, or sepsis
            maternal_causes = [3, 20, 22, 36, 42]
            rankingsrow = vacauselist[i].ranklist
                        
            if sex == 0 or age > 49 or age < 15:
                for cause in maternal_causes:
                    rankingsrow["cause" + str(cause)] = lowest
            
            female_causes = [6, 7]
            if sex == 0:
                for cause in female_causes:
                    rankingsrow["cause" + str(cause)] = lowest
        
            # female, can't have prostate cancer
            if sex == 1:
                rankingsrow["cause39"] = lowest
               
            #can't have AIDS if over 75
            if age > 75:
                rankingsrow["cause1"] = lowest
                rankingsrow["cause2"] = lowest

            # can't have cancer if under 15
            cancers = [6, 7, 9, 17, 27, 30, 39, 43]
            if age < 15:
                for cancer in cancers:
                    rankingsrow["cause" + str(cause)] = lowest

            if self.malaria is None:
                rankingsrow["cause29"] = lowest            
        
        for va in vacauselist:
            for i in range(1, 47):
                if float(va.ranklist["cause"+str(i)]) > float(cutoffs[i-1]):
                    va.ranklist["cause"+str(i)] = lowest
                elif float(va.ranklist["cause"+str(i)]) > float(len(uniformlist) * .18):
                    va.ranklist["cause"+str(i)] = lowest
                elif float(va.causescores["cause"+str(i)]) <= 6.0:  # EXPERIMENT: reject tariff scores less than a fixed amount as well
                    va.ranklist["cause"+str(i)] = lowest

        
        #changing 46 causes to 34 causes:
        causereduction = {'cause1' : '1', 'cause2' : '1', 'cause3' : '21', 'cause4' : '2', 'cause5' : '3', 'cause6' : '4', 'cause7' : '5', 'cause8' : '6', 'cause9' : '7', 'cause10' : '8', 'cause11' : '9', 'cause12' : '9', 'cause13' : '9', 'cause14' : '10', 'cause15' : '11', 'cause16' : '12', 'cause17' : '13', 'cause18' : '14', 'cause19' : '15', 'cause20' : '21', 'cause21' : '16', 'cause22' : '21', 'cause23' : '17', 'cause24' : '22', 'cause25' : '22', 'cause26' : '18', 'cause27' : '19', 'cause28' : '18', 'cause29' : '20', 'cause30' : '25', 'cause31' : '22', 'cause32' : '25', 'cause33' : '23', 'cause34' : '24', 'cause35' : '25', 'cause36' : '21', 'cause37' : '26', 'cause38' : '27', 'cause39' : '28', 'cause40' : '29', 'cause41' : '30', 'cause42' : '21', 'cause43' : '31', 'cause44' : '32', 'cause45' : '33', 'cause46' : '34', 'Undetermined' : ''}
        
        causecounts = {}
        rankwriter = csv.writer(open(self.output_dir + os.sep + 'adult-predictions.csv', 'wb', buffering=0))
        rankwriter.writerow(['sid', 'cause', 'cause34', 'age', 'sex'])    
        for va in vacauselist:
            causescore = lowest
            realcause = 'Undetermined'
            cause34 = ''
            multiple = {}
            for cause in va.ranklist:
                if float(va.ranklist[cause]) < causescore:
                    causescore = float(va.ranklist[cause])
                    realcause = cause
                    cause34 = causereduction[cause]
                    multiple[va.sid] = [cause]
                elif causescore == float(va.ranklist[cause]) and causescore != lowest:
                    multiple[va.sid].append(cause)
            for vakey in multiple.keys():
                if len(multiple[vakey]) > 1:
                    updatestr = "Adult :: WARNING: VA %s had multiple matching results %s, using the first found \n" % (vakey, multiple[vakey])
                    wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
            if cause34 == '':
                cause34 = 'Undetermined'
                if self.iso3 is None:
                    if cause34 in causecounts.keys():
                        causecounts[cause34] = causecounts[cause34] + 1.0
                    else:
                        causecounts[cause34] = 1.0
                else:
                    # for undetermined, look up the values for each cause using keys (age, sex, country) and add them to the 'count' for that cause
                    determined = 0
                    undetermined = 0
                    for uRow in undeterminedmatrix:
                        if uRow[undeterminedheaders.index('sex')] == va.gender and ((int(uRow[undeterminedheaders.index('age')]) >= int(va.age) and int(uRow[undeterminedheaders.index('age')]) < int(va.age)+5) or (int(va.age) > 80 and int(uRow[undeterminedheaders.index('age')]) == 80)) and uRow[undeterminedheaders.index('iso3')] == self.iso3:
                            #get the value and add it
                            if uRow[undeterminedheaders.index('gs_text34')] in causecounts.keys():
                                causecounts[uRow[undeterminedheaders.index('gs_text34')]] = causecounts[uRow[undeterminedheaders.index('gs_text34')]] + float(uRow[undeterminedheaders.index('weight')])
                            else:
                                causecounts[uRow[undeterminedheaders.index('gs_text34')]] = float(uRow[undeterminedheaders.index('weight')])
            else:
                cause34 = adultcauses[cause34]  
                if cause34 in causecounts.keys():
                    causecounts[cause34] = causecounts[cause34] + 1.0
                else:
                    causecounts[cause34] = 1.0
            rankwriter.writerow([va.sid, causereduction[realcause], cause34, va.age, va.gender])
        
        csmfwriter = csv.writer(open(self.output_dir + os.sep + 'adult-csmf.csv', 'wb', buffering=0))
        csmfheaders = ["cause", "CSMF"]
        csmfwriter.writerow(csmfheaders)
        for causekey in causecounts.keys():
            percent = float(causecounts[causekey])/float(sum(causecounts.values()))
            csmfwriter.writerow([causekey, percent])
                    
        # TODO: refactor this test so that it is exercised before
        # merging new pull requests
        # assert int(sum(causecounts.values())) == len(matrix), \
        #              'CSMF must sum to one'
             
        rankwriter = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-ranks.csv', 'wb', buffering=0))
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
            
        tariffwriter = csv.writer(open(self.intermediate_dir + os.sep + 'adult-tariff-scores.csv', 'wb', buffering=0))
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
        
          
        writer.writerow(headers)
        for row in matrix:
            writer.writerow(row)
        
                
        updatestr = "Adult :: Done!\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))             
        return 1   
        
    def round5(self, value):
        return round(value/Decimal(.5))*.5
        
    def abort(self):
        self.want_abort = 1
        
    
        
        
