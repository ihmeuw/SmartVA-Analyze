#!/opt/virtualenvs/ihme-va/bin/pythonw

import csv
import string
import wx
import copy
import workerthread
import os

from symptom_conversions import adult_conversionVars


#variables generated by this step of the procedure
generatedHeaders = ['s88881', 's88882', 's88883', 's88884', 's36991', 's36992', 's18991', 's18992', 's19991', 's19992', 's23991', 's23992', 's23993', 's23994', 's56991', 's56992', 's56993', 's56994', 's55991', 's55992', 's64991', 's64992', 's82991', 's150991', 's150992', 'real_age', 'real_gender']

durationSymptoms = ['age', 's15', 's17', 's22', 's32', 's39', 's41', 's43', 's45', 's50', 's54', 's59', 's67', 's73', 's77', 's81', 's85', 's88', 's90', 's93', 's96', 's99', 's103', 's106', 's125', 's128', 's133', 's147', 's148']

durCutoffs = {'age':49, 's15':30, 's17':5, 's22':10, 's32':15, 's39':22.5, 's41':15, 's43':7, 's45':8, 's50':23.5, 's54':7, 's59':4, 's67':5, 's73':2, 's77':8, 's81':8, 's85':14, 's88':90, 's90':.5416667, 's93':7, 's96':.4166667, 's99':4, 's103':.0208333, 's106':15, 's125':84, 's128':240, 's133':.3541667, 's147':4, 's148':10}

injuries = ['s151', 's152', 's153', 's154', 's155', 's156', 's157', 's159', 's161', 's162']

binaryVars = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14', 's16', 's20', 's21', 's27', 's28', 's29', 's30', 's31', 's33', 's34', 's35', 's37', 's38', 's40', 's42', 's44', 's46', 's47', 's48', 's49', 's51', 's52', 's53', 's58', 's60', 's61', 's63', 's66', 's68', 's69', 's70', 's71', 's72', 's74', 's75', 's76', 's79', 's80', 's84', 's87', 's89', 's92', 's94', 's97', 's98', 's101', 's102', 's104', 's105', 's107', 's109', 's110', 's111', 's112', 's113', 's114', 's115', 's116', 's118', 's119', 's120', 's121', 's122', 's123', 's124', 's126', 's127', 's129', 's130', 's131', 's132', 's134', 's135', 's136', 's137', 's138', 's139', 's140', 's141', 's142', 's143', 's145', 's146', 's149', 's151', 's152', 's153', 's154', 's155', 's156', 's157', 's158', 's159', 's161', 's162']


class AdultSymptomPrep():
    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir

    def run(self):
        reader = csv.reader(open( self.inputFilePath, 'rb'))
        adultwriter = csv.writer(open(self.output_dir + os.sep + 'adult-symptom.csv', 'wb', buffering=0))
        
        updatestr = "Processing adult symptom data\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        
        matrix = list()
        headers = list()
    
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
                
        #Do age thing here first...
        
        #drop unused variables
        keys = adult_conversionVars.keys()
        keys.extend(['s99991', 's999910', 's9999100', 's9999101', 's9999102', 's9999103', 's9999104', 's9999105', 's9999106', 's9999107', 's9999108', 's9999109', 's999911', 's9999110', 's9999111', 's9999112', 's9999113', 's9999114', 's9999115', 's9999116', 's9999117', 's9999118', 's9999119', 's999912', 's9999120', 's9999121', 's9999122', 's9999123', 's9999124', 's9999125', 's9999126', 's9999127', 's9999128', 's9999129', 's999913', 's9999130', 's9999131', 's9999132', 's9999133', 's9999134', 's9999135', 's9999136', 's9999137', 's9999138', 's9999139', 's999914', 's9999140', 's9999141', 's9999142', 's9999143', 's9999144', 's9999145', 's9999146', 's9999147', 's9999148', 's9999149', 's999915', 's9999150', 's9999151', 's9999152', 's9999153', 's9999154', 's9999155', 's9999156', 's9999157', 's9999158', 's9999159', 's999916', 's9999160', 's9999161', 's9999162', 's9999163', 's9999164', 's9999165', 's9999166', 's9999167', 's9999168', 's9999169', 's999917', 's9999170', 's9999171', 's999918', 's999919', 's99992', 's999920', 's999921', 's999922', 's999923', 's999924', 's999925', 's999926', 's999927', 's999928', 's999929', 's99993', 's999930', 's999931', 's999932', 's999933', 's999934', 's999935', 's999936', 's999937', 's999938', 's999939', 's99994', 's999940', 's999941', 's999942', 's999943', 's999944', 's999945', 's999946', 's999947', 's999948', 's999949', 's99995', 's999950', 's999951', 's999952', 's999953', 's999954', 's999955', 's999956', 's999957', 's999958', 's999959', 's99996', 's999960', 's999961', 's999962', 's999963', 's999964', 's999965', 's999966', 's999967', 's999968', 's999969', 's99997', 's999970', 's999971', 's999972', 's999973', 's999974', 's999975', 's999976', 's999977', 's999978', 's999979', 's99998', 's999980', 's999981', 's999982', 's999983', 's999984', 's999985', 's999986', 's999987', 's999988', 's999989', 's99999', 's999990', 's999991', 's999992', 's999993', 's999994', 's999995', 's999996', 's999997', 's999998', 's999999'])
        headers_copy = copy.deepcopy(headers)
        for col in headers_copy:
            if col not in keys:
                index = headers.index(col)
                for row in matrix:
                    del row[index]
                headers.remove(col)
        
        # now convert variable names
        for i, header in enumerate(headers):
            try:
                headers[i] = adult_conversionVars[header]
            except KeyError:
                a = 1  #noop
            
        # add new variables and create space for them in the matrix
        for gen in generatedHeaders:
            headers.append(gen)
            for row in matrix:
                row.append('0')
                            
        # age quartiles
        for row in matrix:
            index = headers.index('age')
            s8881index = headers.index('s88881')
            s8882index = headers.index('s88882')
            s8883index = headers.index('s88883')
            s8884index = headers.index('s88884')
            if int(row[index]) <= 32:
                row[s8881index] = 1
            elif int(row[index]) > 32 and int(row[index]) <= 49:
                row[s8882index] = 1
            elif int(row[index]) > 49 and int(row[index]) <= 65:
                row[s8883index] = 1
            elif int(row[index]) > 65:
                row[s8884index] = 1
                

            # change sex from female = 2, male = 1 to female = 1, male = 0
            # if unkonwn sex will default to 0 so it does not factor into analysis
            index = headers.index('sex')
            val = int(row[index])
            if val == 2:
                row[index] = 1
            elif val == 1:
                row[index] = 0
            elif val == 9:
                row[index] = 0
                
            #make new variables to store the real age and gender, but do it after we've modified the sex vars from 2, 1 to 1, 0
            ageindex = headers.index('real_age')
            genderindex = headers.index('real_gender')
            row[ageindex] = row[headers.index('age')]
            row[genderindex] = row[headers.index('sex')]
                
            for sym in durationSymptoms:
                index = headers.index(sym)
                #replace the duration with 1000 if it is over 1000 and not missing
                if row[index] == '':
                    row[index] = 0
                elif float(row[index]) > 1000:
                    row[index] = 1000
                # use cutoffs to determine if they will be replaced with a 1 (were above or equal to the cutoff)
                if float(row[index]) >= durCutoffs[sym] and row[index] != str(0):
                    row[index] = 1
                else:
                    row[index] = 0
                    
	        # The "varlist" variables in the loop below are all indicators for different questions about injuries (road traffic, fall, fires)
	        # We only want to give a VA a "1"/yes response for that question if the injury occured within 30 days of death (i.e. s163<=30)
	        # Otherwise, we could have people who responded that they were in a car accident 20 years prior to death be assigned to road traffic deaths
	        for injury in injuries:
	            index = headers.index(injury)
	            injury_cut_index = headers.index('s163')
	            # 30 is the injury cutoff         
	            if float(row[injury_cut_index]) > 30:
	                row[index] = 0


            #dichotimize!
            index1 = headers.index('s36991')
            index2 = headers.index('s36992')
            val = row[headers.index('s36')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if (val == 1):
                row[index1] = 1
            elif (val == 2 or val == 3):
                row[index2] = 1
                
            index1 = headers.index('s18991')
            index2 = headers.index('s18992')
            val = row[headers.index('s18')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if (val == 1):
                row[index1] = 1
            elif (val == 2 or val == 3):
                row[index2] = 1
                
            index1 = headers.index('s19991')
            index2 = headers.index('s19992')
            val = row[headers.index('s19')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if (val == 1):
                row[index1] = 1
            elif (val == 2):
                row[index2] = 1
            
                
            index1 = headers.index('s23991')
            index2 = headers.index('s23992')
            index3 = headers.index('s23993')
            index4 = headers.index('s23994')
            s23val = row[headers.index('s23')]
            s25val = row[headers.index('s25')]
            if s23val == '':
                s23val = 0
            else:
                s23val = int(s23val)
            if s25val == '':
                s25val = 0
            else:
                s25val = int(s25val)
            if s23val == 1 or s25val == 1:
                row[index1] = 1
            if s23val == 2 or s25val == 2:
                row[index2] = 1
            if s23val == 3 or s25val == 3:
                row[index3] = 1
            if s23val == 4 or s25val == 4:
                row[index4] = 1
                 
            #s56 can be multiple    
            index1 = headers.index('s56991')
            index2 = headers.index('s56992')
            index3 = headers.index('s56993')
            index4 = headers.index('s56994')
            val = row[headers.index('s56')]
            if val == '':
                val = ['0']
            else:
                val = val.split(' ')
                
                
                #this one doesn't exist?
            # val2 = row[headers.index('s57')]
            #            if val2 == '':
            #                val2 = 0
            #            else:
            #                val2 = int(val2)
            # if (val == 1 or val2 == 1):
            #                 row[index1] = 1
            #             elif (val == 2 or val2 == 2):
            #                 row[index2] = 1
            #             elif (val == 3 or val2 == 3):
            #                 row[index3] = 1
            #             elif (val == 4 or val2 == 4):
            #                 row[index4] = 1

            if '1' in val:
                row[index1] = 1
            if '2' in val:
                row[index2] = 1
            if '3' in val:
                row[index3] = 1
            if '4' in val:
                row[index4] = 1
            
            index1 = headers.index('s55991')
            index2 = headers.index('s55992')
            val = row[headers.index('s55')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if (val == 1):
                row[index1] = 1
            elif val == 2:
                row[index2] = 1
            
            val = row[headers.index('s62')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if val == 1 or val == 2 or val == 8 or val == 9 or val == 0:
                row[headers.index('s62')] = 0
            elif val == 3:
                row[headers.index('s62')] = 1
                
            index1 = headers.index('s64991')
            index2 = headers.index('s64992')
            val = row[headers.index('s64')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if (val == 1 or val == 2):
                row[index1] = 1
            elif (val == 3):
                row[index2] = 1
      
            val = row[headers.index('s78')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if val == 1 or val == 2 or val == 8 or val == 9 or val == 0:
                row[headers.index('s78')] = 0
            elif val == 3:
                row[headers.index('s78')] = 1
      
            index1 = headers.index('s82991')
            val = row[headers.index('s82')]
            if val == '':
                val = 0
            else:
                val = int(val)
            
            #not in electronic?
            # val2 = row[headers.index('s83')]
            #             if val2 == '':
            #                 val2 = 0
            #             else:
            #                 val2 = int(val2)
            #             if (val == 2 or val2 == 2):
            #                 row[index1] = 1
            if val == 2:
                row[index1] = 1
 
      
            val = row[headers.index('s86')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if val == 1 or val == 8 or val == 9 or val == 0:
                row[headers.index('s86')] = 0
            elif val == 2:
                row[headers.index('s86')] = 1
                
            val = row[headers.index('s91')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if val == 2 or val == 8 or val == 9 or val == 0:
                row[headers.index('s91')] = 0
                
            val = row[headers.index('s95')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if val == 2 or val == 8 or val == 9 or val == 0:
                row[headers.index('s95')] = 0

            val = row[headers.index('s100')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if val == 2 or val == 8 or val == 9 or val == 0:
                row[headers.index('s100')] = 0

      
            index1 = headers.index('s150991')
            index2 = headers.index('s150992')
            val = row[headers.index('s150')]
            if val == '':
                val = 0
            else:
                val = int(val)
            if (val == 1):
                row[index1] = 1
            elif (val == 2 or val == 3):
                row[index2] = 1
      
            # TODO: type?
            if row[headers.index('s107')] == str(1) or row[headers.index('s108')] == str(1):
                row[headers.index('s107')] = 1
      
            # ensure all binary variables actually ARE 0 or 1:
            for bin in binaryVars:
                val = row[headers.index(bin)]
                if val == '' or int(val) != 1:
                    row[headers.index(bin)] = 0
                    
        
        droplist = ['s163', 's36', 's18', 's19', 's23', 's25', 's56', 's55', 's64', 's82', 's150', 's108']
        for d in droplist:
            index = headers.index(d)
            headers.remove(d)
            for row in matrix:
                del row[index]
        
        
        adultwriter.writerow(headers)
        for row in matrix:
            adultwriter.writerow(row)
        
                
                    
        return 1    	
        
        