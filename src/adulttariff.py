#!/opt/virtualenvs/ihme-va/bin/pythonw

import csv
import string
import wx
import copy
import math
import random
from decimal import Decimal
import workerthread
import os
import sys
import platform

#excel function..  =INDEX(B$1:D$1,MATCH(MIN(B2:D2),B2:D2,0))

# data structure we use to keep track of an manipulate data
class ScoredVA:
    def __init__(self, causescores, cause, sid):
        self.causescores = causescores #dict of {"cause1" : value, "cause2" :...}
        self.cause = cause #int
        self.ranklist = {}
        self.sid = sid
            

class Tariff():
    def __init__(self, notify_window, input_file, output_dir):
        self.inputFilePath = input_file
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir
        

    def run(self):
        reader = csv.reader(open( self.inputFilePath, 'rb'))
        writer = csv.writer(open(self.output_dir + os.sep + 'adult-tariff-results.csv', 'wb', buffering=0))
        
        updatestr = "Processing tariffs on adults\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        
        
        tarifffile = 'tariffs-adult.csv'
        validatedfile = 'validated-adult.csv'
        if platform.system() == "Windows":
            tarifffile = os.path.join(os.path.dirname(sys.executable), 'tariffs-adult.csv')
            validatedfile = os.path.join(os.path.dirname(sys.executable), 'validated-adult.csv')
        
        tariffreader = csv.reader(open(tarifffile, 'rU'))
        validatedreader = csv.reader(open(validatedfile, 'rU'))
        
        
        
        matrix = list()
        headers = list()
        
        tariffheaders = list()
        tariffmatrix = list()
        
        validatedheaders = list()
        validatedmatrix = list()
    
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
            #print "sorted dict %s" % sorteddict

            slist = []
            for val in sorteddict[:40]:
                slist.append(val[0])
            cause40s[cause] = slist
        
        for cause in cause40s.keys():
            asdf = cause40s[cause]
            asdf.sort()
        
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
            va = ScoredVA(causedict, row[validatedheaders.index('va46')], sid)
            vacauselist.append(va)
            
       
        updatestr = "Creating validated causelist.  (This takes a few minutes)\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))    
        # creates a list of causes/scores for each VALIDATED va.
        # va1 :: cause1/score, cause2/score...casue46/score
        # ... 
        
        #print tariffmatrix[0]
        
        vavalidatedcauselist = []
        for i, row in enumerate(validatedmatrix):
            causedict = {}
            for causenum in range(1,47):
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
            va = ScoredVA(causedict, row[validatedheaders.index('va46')], sid)
            vavalidatedcauselist.append(va)
                    
        #print "len causelist %s" % (len(vavalidatedcauselist))
        #print "validated va1 = %s" % vavalidatedcauselist[1]
            

        updatestr = "Creating uniform training set\n"
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
        
                                
        #print "sample %s" % samplesize        
        #create new uniform training set such that each cause has samplessize VAs
        random.seed(123)
        uniformtrain = {}
        for cause in range(1, 47):
            uniformtrain[str(cause)] = []
            #indexes of all VAs of a certain cause
            for causeindex in causeindexes[str(cause)]:
                # first add all of the VAs per cause to make sure they're included at least once
                uniformtrain[str(cause)].append(vavalidatedcauselist[causeindex])
            # fill the rest so it gets up to sample size
            for i in range(len(causeindexes[str(cause)]), samplesize):
                #print validatedmatrix[choice(causeindexes[str(cause)])]
                uniformtrain[str(cause)].append(vavalidatedcauselist[random.choice(causeindexes[str(cause)])])

        vas = []
        for row in uniformtrain['1']:
            vas.append(row.sid)
        asdf = vas.sort()
        print asdf
        
        
        # uniform train
        # key == 1, 2, 3 (causes)
        # uniformtrain["1"] == [ScoredVA1, ScoredVA2]
        # where uniformtrain["1"] has 630 VAs, each with 46 causes/scores.
               
        # print "WTF: %s" % uniformtrain["1"][1]        
        #         
        #         print "keys %s" % uniformtrain.keys()
        #         #print "uni1 %s" % uniformtrain["1"]
        #         print "len of cause1 %s" % len(uniformtrain["1"])  
        #         print "woot"
        #         print "asdf %s" % uniformtrain["1"]
        #for a in uniformtrain["1"]:
        #    print a      
        
        
        
        #TODO HERE.  Bet I have to compare all the causes, not just the ones in mylist
        
#         Then I generate rankings for my external data set:
#         for each external VA:
#         for each cause:
#           get the external calculated tariff for this cause (death score)

#           for all the VAs in the uniform training set with this cause (630), get the all the tariffs (630*46 = around ~28k), and sort them from greatest to least

# Here is the difference- We should be using all of the VAs in the uniform training set, not just the tariff scores for the 630 VAs from this cause. And we should be looking at the tariff scores for this cause for all 28k VAs. i.e. we should be ranking the external VAs against the 28k scores for cause n regardless of gold standard cause of death.

        # create a list of ALL the VAs in our uniform set
        uniformlist = []
        for key in uniformtrain.keys():
            # vas this should be 600ish long
            vas = uniformtrain[key]
            for va in vas:
                uniformlist.append(va)
        
        
        updatestr = "Generating cause rankings. (This takes a few minutes)\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

        for va in vacauselist:
            sortedtariffs = []
            ranklist = {}
            for i in range(1, 47):
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
                minval = 10000
                
                # loop through all the new scores, find the minimum value, store that index
                # if there are multiple minimum values that are the same, take the mean of the indexes
                for index, val in enumerate(sortedtariffs):
                    #print "trying %s and %s" % (index, val)
                    if val < minval:
                        minval = val
                        minlist = [index]
                    elif val == minval:
                        minlist.append(index)
                
                index = sum(minlist)/float(len(minlist))
                ranklist[cause] = index
            va.ranklist = ranklist
            
        rankwriter = csv.writer(open(self.output_dir + os.sep + 'adult-external-ranks.csv', 'wb', buffering=0))
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
#                OrderedDict(sorted(d.items(), key=lambda t: t[1]))
#OrderedDict([('pear', 1), ('orange', 2), ('banana', 3), ('apple', 4)])
            #sortedcauselist = sorted(causelist, key=lambda t:(t[1]), reverse=True)
            #sortedcaustlist = sorted(causelist.items(), key=lambda t: t[1], reverse=True)
            #sorted(sdict.items(), key=lambda t: t[1], reverse=True)
            
            # now have a sorted list of sid, causescore for a specific cause
            
            for j, item in enumerate(sortedcauselist):
                #item[2] == va
                item[2].ranklist[cause] = j
                
        
                        
        # va = uniformlist[0]
        # print va.sid
        # print va.ranklist
        # 
        # 
        # va = uniformlist[1]
        # print va.sid
        # print va.ranklist
        # 
        # va = uniformlist[2]
        # print va.sid
        # print va.ranklist
                
        
        #Lines 403-409 in the Stata code generate the ranks for the validation data. It takes in the 27,000x46 tariff scores for the validation data and then goes cause by cause and sorts the tariff scores for one cause from highest to lowest and then generates a new variable called "rank" that holds the position of the VA on the list after being sorted:

        
                
        #print "uniformlistlen %s" % len(uniformlist)
        
        #print "uniformlist[] %s" % uniformlist[0]
        
        updatestr = "Generating cutoffs\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        
        cutoffs = []
        for i in range(1, 47):
            causelist = []
            for va in uniformlist:
                causelist.append([va.cause, va.causescores["cause" + str(i)], va.sid, va])
            #print "causelistlen = %s" % (len(causelist))
            #print "causelist = %s" % causelist
            sortedlist = sorted(causelist, key=lambda t: (t[1], t[2]), reverse=True)
            #print "sortedlistlen %s" % len(sortedlist)
            #print "ALSDKFJSLKDFJSLDKJF %s" % sortedlist
            
            #print "SORTEDLIST %s" % sortedlist

            locallist = []
            for j, va in enumerate(sortedlist):
                #0 == actualcause
                #print "va[0] == %s" % va[0]
                if va[0] == str(i):
                    #print "adding index %s" % j
                    # j is the "rank"
                    locallist.append(j)
            index = int(len(locallist) * .89)
            #print "trying index %s" % index
            #print "locallistlen %s" % len(locallist)
            #print locallist
            cutoffs.append(locallist[index])
        
                        
        f = open(self.output_dir + os.sep + 'adult-cutoffs.txt','w')
        for i, cutoff in enumerate(cutoffs):
            f.write(str(i+1) + " : " + str(cutoff) + "\n")
        f.close()
        
        # lowest rank is actually the biggest number
        lowest = 0
        # find the lowest rank and then add 1 to it
        for va in vacauselist:
            for cause in va.ranklist.keys():
                if float(va.ranklist[cause]) > 0 and float(va.ranklist[cause]) > lowest:
                        print "lowest found for cause %s in coda %s" % (va.sid, cause)
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
        
            # female, can't be prostate cancer
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

            #cutoff = 89
            #abs_cutoff = .18
            
        
        for va in vacauselist:
            for i in range(1, 47):
                if float(va.ranklist["cause"+str(i)]) > float(cutoffs[i-1]):
                    va.ranklist["cause"+str(i)] = lowest
                elif float(va.ranklist["cause"+str(i)]) > float(len(uniformlist) * .18):
                    va.ranklist["cause"+str(i)] = lowest
                    
        
        #changing 46 causes to 34 causes:
        causereduction = {'cause1' : '1', 'cause2' : '1', 'cause3' : '21', 'cause4' : '2', 'cause5' : '3', 'cause6' : '4', 'cause7' : '5', 'cause8' : '6', 'cause9' : '7', 'cause10' : '8', 'cause11' : '9', 'cause12' : '9', 'cause13' : '9', 'cause14' : '10', 'cause15' : '11', 'cause16' : '12', 'cause17' : '13', 'cause18' : '14', 'cause19' : '15', 'cause20' : '21', 'cause21' : '16', 'cause22' : '21', 'cause23' : '17', 'cause24' : '22', 'cause25' : '22', 'cause26' : '18', 'cause27' : '19', 'cause28' : '18', 'cause29' : '20', 'cause30' : '25', 'cause31' : '22', 'cause32' : '25', 'cause33' : '23', 'cause34' : '24', 'cause35' : '25', 'cause36' : '21', 'cause37' : '26', 'cause38' : '27', 'cause39' : '28', 'cause40' : '29', 'cause41' : '30', 'cause42' : '21', 'cause43' : '31', 'cause44' : '32', 'cause45' : '33', 'cause46' : '34'}
        
        
        rankwriter = csv.writer(open(self.output_dir + os.sep + 'adult-tariff-causes.csv', 'wb', buffering=0))
        rankwriter.writerow(['sid', 'cause', 'cause34'])    
        for va in vacauselist:
            causescore = lowest
            causelist = []
            causereductionlist = []
            for cause in va.ranklist:
                if float(va.ranklist[cause]) < causescore:
                    causescore = float(va.ranklist[cause])
                    causelist = [cause]
                    causereductionlist = [causereduction[cause]]
                elif causescore == float(va.ranklist[cause]):
                    causelist.append(cause)
                    causereductionlist.append(causereduction[cause])
            rankwriter.writerow([va.sid, causelist, causereductionlist])
                    
        
        
        
                    
        
        # rankings is a list of VAs, and for each va you have {cause, rank}

        
        # ff = uniformtrain["1"].values()
        #        sortedff = sorted(ff, reverse=True)
        #        subt = []
        #        for val in sortedff:
        #            subt.append(math.fabs(val - deathscore))
        
        
        rankwriter = csv.writer(open(self.output_dir + os.sep + 'adult-tariff-ranks.csv', 'wb', buffering=0))
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
            
        tariffwriter = csv.writer(open(self.output_dir + os.sep + 'adult-tariff-scores.csv', 'wb', buffering=0))
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
        
        
        
        
        
        
                            
            #     for cause in cause40s:
            #         print cause
                    # for svar in cause:
                    #                        index = headers.index(svar)
                    #                        if row[index] == 1:
                    #                            tariff
            # make list of causes per va?
            # for each va
            # for each cause40
            # if s in cause40 is '1' in va, then get score from tariff and add it to the cause
            
            # when done, have causelist of 46 with scores for each cause for each VA
        
        
        
      
        
        
        
        
        
        
        
        
        #end
        
        writer.writerow(headers)
        for row in matrix:
            writer.writerow(row)
        
                
                    
        return 1   
        
    def round5(self, value):
        return round(value/Decimal(.5))*.5
        
    
        
        