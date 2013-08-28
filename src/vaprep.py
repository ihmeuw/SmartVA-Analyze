#!/opt/virtualenvs/ihme-va/bin/pythonw

# This file cleans up input and converts from ODK collected data to VA variables

import csv
import string
import wx
import os
import workerthread

# Thread class that executes processing
class VaPrep():
    """Worker Thread Class."""
    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir

    def run(self):
        # read stocks data, print status messages
        reader = csv.reader(open( self.inputFilePath, 'rU'))
        
        adultwriter = csv.writer(open(self.output_dir + os.sep + 'adult-prepped.csv', 'wb', buffering=0))
        childwriter = csv.writer(open(self.output_dir + os.sep + 'child-prepped.csv', 'wb', buffering=0))
        neonatewriter = csv.writer(open(self.output_dir + os.sep + 'neonate-prepped.csv', 'wb', buffering=0))
          
        # these are new column headers that we generate since they are not already in the ODK data.
        # any newly created variables at this step should be added here      
        additionalHeaders = ["adultparalysis1", "adultparalysis2", "adultparalysis3", "adultparalysis4", "adultparalysis5", "adultparalysis6", "adultparalysis7", "adultparalysis8", "adultparalysis9", "adultparalysis10", "adultinjury1", "adultinjury2", "adultinjury3", "adultinjury4", "adultinjury5", "adultinjury6", "adultinjury7", "adultinjury8", "childinjury1", "childinjury2", "childinjury3", "childinjury4", "childinjury5", "childinjury6", "childinjury7", "childinjury8", "childinjury9", "childinjury10", "adultrash1", "adultrash2", "adultrash3", "childabnorm1", "childabnorm2", "childabnorm3", "childabnorm4", "childabnorm5", "childabnorm31", "childabnorm32", "childabnorm33", "childabnorm34", "childabnorm35", "complications1", "complications2", "complications3", "complications4", "complications5", "complications6", "complications7", "complications8", "complications9", "complications10", "complications11", "complications12", "provider1", "provider2", "provider3", "provider4", "provider5", "provider6", "provider7", "provider8", "provider9", "provider10", "provider11", "provider12", "provider13", "provider14", 's99991', 's999910', 's9999100', 's9999101', 's9999102', 's9999103', 's9999104', 's9999105', 's9999106', 's9999107', 's9999108', 's9999109', 's999911', 's9999110', 's9999111', 's9999112', 's9999113', 's9999114', 's9999115', 's9999116', 's9999117', 's9999118', 's9999119', 's999912', 's9999120', 's9999121', 's9999122', 's9999123', 's9999124', 's9999125', 's9999126', 's9999127', 's9999128', 's9999129', 's999913', 's9999130', 's9999131', 's9999132', 's9999133', 's9999134', 's9999135', 's9999136', 's9999137', 's9999138', 's9999139', 's999914', 's9999140', 's9999141', 's9999142', 's9999143', 's9999144', 's9999145', 's9999146', 's9999147', 's9999148', 's9999149', 's999915', 's9999150', 's9999151', 's9999152', 's9999153', 's9999154', 's9999155', 's9999156', 's9999157', 's9999158', 's9999159', 's999916', 's9999160', 's9999161', 's9999162', 's9999163', 's9999164', 's9999165', 's9999166', 's9999167', 's9999168', 's9999169', 's999917', 's9999170', 's9999171', 's999918', 's999919', 's99992', 's999920', 's999921', 's999922', 's999923', 's999924', 's999925', 's999926', 's999927', 's999928', 's999929', 's99993', 's999930', 's999931', 's999932', 's999933', 's999934', 's999935', 's999936', 's999937', 's999938', 's999939', 's99994', 's999940', 's999941', 's999942', 's999943', 's999944', 's999945', 's999946', 's999947', 's999948', 's999949', 's99995', 's999950', 's999951', 's999952', 's999953', 's999954', 's999955', 's999956', 's999957', 's999958', 's999959', 's99996', 's999960', 's999961', 's999962', 's999963', 's999964', 's999965', 's999966', 's999967', 's999968', 's999969', 's99997', 's999970', 's999971', 's999972', 's999973', 's999974', 's999975', 's999976', 's999977', 's999978', 's999979', 's99998', 's999980', 's999981', 's999982', 's999983', 's999984', 's999985', 's999986', 's999987', 's999988', 's999989', 's99999', 's999990', 's999991', 's999992', 's999993', 's999994', 's999995', 's999996', 's999997', 's999998', 's999999']

        updatestr = "Initial data prep\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        
        first = 1
        
        # matrix is a list of lists containing all of our data
        matrix = list()
        
        # column headers
        headers = list()
    
        for row in reader:
            if first == 1:
                # if reading the first row, add to the column headers
                for col in row:    
                    headers.append(col)
                first = 0
                
                # now add the headers that we create from additionalHeaders
                for head in additionalHeaders:
                    headers.append(head)
                    
            else:
                # if it's not the first row, create spaces in the current row to match additionalHeaders, then add the row to our matrix
                for head in additionalHeaders:
                    row.append("0")
                matrix.append(row)
                                    
        
        ### column header renaming
        # rename adult_2_87 adult287
        index = headers.index("adult_2_87")
        headers[index] = "orgadult287"
              
        #rename adult_5_2 adult52
        index = headers.index("adult_5_2")
        headers[index] = "orgadult52" 
        
        #rename child_4_48 orgchild448
        index = headers.index("child_4_48")
        headers[index] = "orgchild448"        
        
        #rename child_1_19 to child119
        index = headers.index("child_1_19")
        headers[index] = "child119"
        
        #rename child_1_19a to child119a
        index = headers.index("child_1_19a")
        headers[index] = "child119a"
       
        #rename child_3_3 child33
        index = headers.index("child_3_3")
        headers[index] = "orgchild33"
        
        #rename child_2_1 child21
        index = headers.index("child_2_1")
        headers[index] = "orgchild21"
                
        #rename child_5_2 child52
        index = headers.index("child_5_2")
        headers[index] = "child52"
        
        # loop through each row, updating values (mostly additionalHeaders), based on user's answers
        for row in matrix:
            # fill in blank values for age
            index = headers.index("gen_5_4a")
            if row[index] == "":
                row[index] = 0
            index = headers.index("gen_5_4b")
            if row[index] == "":
                row[index] = 0
            index = headers.index("gen_5_4c")
            if row[index] == "":
                row[index] = 0
            
            # set paralysis variables based on multiple choice question
            index = headers.index("orgadult287")
            val = row[index].split(' ')
            if str(1) in val:
                subindex = headers.index("adultparalysis1")
                row[subindex] = 1
            if str(2) in val:
                subindex = headers.index("adultparalysis2")
                row[subindex] = 1
            if str(3) in val:
                subindex = headers.index("adultparalysis3")
                row[subindex] = 1
            if str(4) in val:
                subindex = headers.index("adultparalysis4")
                row[subindex] = 1
            if str(5) in val:
                subindex = headers.index("adultparalysis5")
                row[subindex] = 1
            if str(6) in val:
                subindex = headers.index("adultparalysis6")
                row[subindex] = 1
            if str(7) in val:
                subindex = headers.index("adultparalysis7")
                row[subindex] = 1
            if str(8) in val:
                subindex = headers.index("adultparalysis8")
                row[subindex] = 1
            if str(9) in val:
                subindex = headers.index("adultparalysis9")
                row[subindex] = "1"
            if str(11) in val:
                subindex = headers.index("adultparalysis10")
                row[subindex] = 1
            
            # set adultinjury variables based on multiple choice question
            index = headers.index("orgadult52")
            val = row[index].split(' ')    
            if str(1) in val:
                subindex = headers.index("adultinjury1")
                row[subindex] = 1
            if str(2) in val:
                subindex = headers.index("adultinjury2")
                row[subindex] = 1
            if str(3) in val:
                subindex = headers.index("adultinjury3")
                row[subindex] = 1
            if str(4) in val:
                subindex = headers.index("adultinjury4")
                row[subindex] = 1
            if str(5) in val:
                subindex = headers.index("adultinjury5")
                row[subindex] = 1
            if str(6) in val:
                subindex = headers.index("adultinjury6")
                row[subindex] = 1
            if str(7) in val:
                subindex = headers.index("adultinjury7")
                row[subindex] = 1
            if str(11) in val:
                subindex = headers.index("adultinjury8")
                row[subindex] = 1
            
            # set childinjury variables based on multiple choice question
            index = headers.index("orgchild448")
            val = row[index].split(' ')
            if str(1) in val:
                subindex = headers.index("childinjury1")
                row[subindex] = 1
            if str(2) in val:
                subindex = headers.index("childinjury2")
                row[subindex] = 1
            if str(3) in val:
                subindex = headers.index("childinjury3")
                row[subindex] = 1
            if str(4) in val:
                subindex = headers.index("childinjury4")
                row[subindex] = 1
            if str(5) in val:
                subindex = headers.index("childinjury5")
                row[subindex] = 1
            if str(6) in val:
                subindex = headers.index("childinjury6")
                row[subindex] = 1
            if str(7) in val:
                subindex = headers.index("childinjury7")
                row[subindex] = 1
            if str(11) in val:
                subindex = headers.index("childinjury8")
                row[subindex] = 1
            if str(8) in val:
                subindex = headers.index("childinjury9")
                row[subindex] = 1
            if str(9) in val:
                subindex = headers.index("childinjury10")
                row[subindex] = 1
            
            
            # set adultrash variables based on multiple choice question            
            index = headers.index("adult_2_9")
            val = row[index].split(' ')
            adultrash1index = headers.index("adultrash1")
            adultrash2index = headers.index("adultrash2")
            adultrash3index = headers.index("adultrash3")

            # this is a little weird.
            # basically if 1, 2, and 3 are selected, then change the value to 4 (all)
            if str(1) in val and str(2) in val and str(3) in val:
                # first see if anything else is selected
                row[index] = 4
                row[adultrash1index] = 4
            else:
                #otherwise set adultrashN to the other selected values
                words = row[index].split(' ')
                if len(words) == 1:
                    row[adultrash1index] = words[0]
                if len(words) == 2:
                    row[adultrash1index] = words[0]
                    row[adultrash2index] = words[1]
                if len(words) == 3:
                    row[adultrash1index] = words[0]
                    row[adultrash2index] = words[1]
                    row[adultrash3index] = words[2]

            
            #set child abnormality values
            index = headers.index("child119")
            first = row[index].split(' ')
            index = headers.index("child119a")
            second = row[index].split(' ')
            
            if str(1) in first or str(1) in second:
                subindex = headers.index("childabnorm1")
                row[subindex] = 1
            if str(2) in first or str(2) in second:
                subindex = headers.index("childabnorm2")
                row[subindex] = 1
            if str(3) in first or str(3) in second:
                subindex = headers.index("childabnorm3")
                row[subindex] = 1
            if str(11) in first or str(11) in second:
                subindex = headers.index("childabnorm4")
                row[subindex] = 1
            if str(8) in first or str(8) in second:
                subindex = headers.index("childabnorm5")
                row[subindex] = 1
                
            #set child abnormality values
            index = headers.index("orgchild33")
            val = row[index].split(' ')
            if str(1) in val:
                subindex = headers.index("childabnorm31")
                row[subindex] = 1
            if str(2) in val:
                subindex = headers.index("childabnorm32")
                row[subindex] = 1
            if str(3) in val:
                subindex = headers.index("childabnorm33")
                row[subindex] = 1
            if str(11) in val:
                subindex = headers.index("childabnorm34")
                row[subindex] = 1
            if str(8) in val:
                subindex = headers.index("childabnorm35")
                row[subindex] = 1
            
            # set complications values
            index = headers.index("orgchild21")
            val = row[index].split(' ')
            if str(1) in val:
                subindex = headers.index("complications1")
                row[subindex] = 1
            if str(2) in val:
                subindex = headers.index("complications2")
                row[subindex] = 1
            if str(3) in val:
                subindex = headers.index("complications3")
                row[subindex] = 1
            if str(4) in val:
                subindex = headers.index("complications4")
                row[subindex] = 1
            if str(5) in val:
                subindex = headers.index("complications5")
                row[subindex] = 1
            if str(6) in val:
                subindex = headers.index("complications6")
                row[subindex] = 1
            if str(7) in val:
                subindex = headers.index("complications7")
                row[subindex] = 1
            if str(8) in val:
                subindex = headers.index("complications8")
                row[subindex] = 1
            if str(9) in val:
                subindex = headers.index("complications9")
                row[subindex] = 1
            if str(10) in val:
                subindex = headers.index("complications10")
                row[subindex] = 1
            if str(88) in val:
                subindex = headers.index("complications11")
                row[subindex] = 1
            if str(99) in val:
                subindex = headers.index("complications12")
                row[subindex] = 1
                
            
            # set provider values
            index = headers.index("child52")
            val = row[index].split(' ')
            if str(1) in val:
                subindex = headers.index("provider1")
                row[subindex] = 1
            else:
                subindex = headers.index("provider1")
                row[subindex] = 0
            if str(2) in val:
                subindex = headers.index("provider2")
                row[subindex] = 1
            else:
                subindex = headers.index("provider2")
                row[subindex] = 0
            if str(3) in val:
                subindex = headers.index("provider3")
                row[subindex] = 1
            else:
                subindex = headers.index("provider3")
                row[subindex] = 0
            if str(4) in val:
                subindex = headers.index("provider4")
                row[subindex] = 1
            else:
                subindex = headers.index("provider4")
                row[subindex] = 0
            if str(5) in val:
                subindex = headers.index("provider5")
                row[subindex] = 1
            else:
                subindex = headers.index("provider5")
                row[subindex] = 0
            if str(6) in val:
                subindex = headers.index("provider6")
                row[subindex] = 1
            else:
                subindex = headers.index("provider6")
                row[subindex] = 0
            if str(7) in val:
                subindex = headers.index("provider7")
                row[subindex] = 1
            else:
                subindex = headers.index("provider7")
                row[subindex] = 0
            if str(8) in val:
                subindex = headers.index("provider8")
                row[subindex] = 1
            else:
                subindex = headers.index("provider8")
                row[subindex] = 0
            if str(9) in val:
                subindex = headers.index("provider9")
                row[subindex] = 1
            else:
                subindex = headers.index("provider9")
                row[subindex] = 0
            if str(10) in val:
                subindex = headers.index("provider10")
                row[subindex] = 1
            else:
                subindex = headers.index("provider10")
                row[subindex] = 0
            if str(11) in val:
                subindex = headers.index("provider11")
                row[subindex] = 1
            else:
                subindex = headers.index("provider11")
                row[subindex] = 0
            if str(12) in val:
                subindex = headers.index("provider12")
                row[subindex] = 1
            else:
                subindex = headers.index("provider12")
                row[subindex] = 0
            if str(88) in val:
                subindex = headers.index("provider13")
                row[subindex] = 1
            else:
                subindex = headers.index("provider13")
                row[subindex] = 0
            if str(99) in val:
                subindex = headers.index("provider14")
                row[subindex] = 1
            else:
                subindex = headers.index("provider14")
                row[subindex] = 0
                
            #weights
            index = headers.index("child_1_8")
            val = row[index]   
            index18a = headers.index("child_1_8a")
            index18b = headers.index("child_1_8b") 
            if val == str(2):
                row[index18a] = float(row[index18b]) * 1000
                row[index] = 1
            
            index = headers.index("child_5_6e")
            val = row[index]    
            if val == str(2):
                index56f = headers.index("child_5_6f")
                index56g = headers.index("child_5_6g")
                row[index56f] = float(row[index56g]) * 1000
                row[index] = 1
            
            index = headers.index("child_5_7e")
            val = row[index]    
            if val == str(2):
                index57f = headers.index("child_5_7f")
                index57g = headers.index("child_5_7g")
                row[index57f] = float(row[index57g]) * 1000
                row[index] = 1

        # end loop
        
        # keepColumns = ['sid', 'gen_2_1', 'gen_2_2a', 'gen_3_1', 'gen_4_2', 'gen_4_3', 'gen_4_4', 'gen_4_5', 'gen_4_6', 'gen_4_7', 'gen_4_8', 'gen_5_1c', 'gen_5_1b', 'gen_5_1a', 'gen_5_2', 'gen_5_3c', 'gen_5_3b', 'gen_5_3a', 'gen_5_4a', 'gen_5_4b', 'gen_5_4c', 'gen_5_5', 'gen_5_6', 'gen_5_7', 'gen_5_8', 'adult_1_1a', 'adult_1_1b', 'adult_1_1c', 'adult_1_1d', 'adult_1_1e', 'adult_1_1f', 'adult_1_1g', 'adult_1_1h', 'adult_1_1i', 'adult_1_1j', 'adult_1_1k', 'adult_1_1l', 'adult_1_1m', 'adult_1_1n', 'adult_2_1', 'adult_2_2', 'adult_2_3', 'adult_2_3a', 'adult_2_4', 'adult_2_5', 'adult_2_6', 'adult_2_7', 'adult_2_8', 'adult_2_8a', 'adultrash1', 'adult_2_9a', 'adultrash2', 'adultrash3', 'adult_2_10', 'adult_2_11', 'adult_2_12', 'adult_2_13', 'adult_2_14', 'adult_2_15', 'adult_2_15a', 'adult_2_16', 'adult_2_17', 'adult_2_18', 'adult_2_19', 'adult_2_20', 'adult_2_21', 'adult_2_22', 'adult_2_23', 'adult_2_24', 'adult_2_25', 'adult_2_26', 'adult_2_27', 'adult_2_28', 'adult_2_29', 'adult_2_30', 'adult_2_31', 'adult_2_32', 'adult_2_33', 'adult_2_34', 'adult_2_35', 'adult_2_36', 'adult_2_37', 'adult_2_38', 'adult_2_39', 'adult_2_40', 'adult_2_41', 'adult_2_42', 'adult_2_43', 'adult_2_44', 'adult_2_45', 'adult_2_46', 'adult_2_46a', 'adult_2_47', 'adult_2_48', 'adult_2_48a', 'adult_2_49', 'adult_2_50', 'adult_2_51', 'adult_2_52', 'adult_2_53', 'adult_2_54', 'adult_2_55', 'adult_2_56', 'adult_2_57', 'adult_2_58', 'adult_2_59', 'adult_2_60', 'adult_2_61', 'adult_2_62', 'adult_2_63', 'adult_2_64', 'adult_2_65', 'adult_2_66', 'adult_2_67', 'adult_2_68', 'adult_2_69', 'adult_2_70', 'adult_2_71', 'adult_2_72', 'adult_2_73', 'adult_2_74', 'adult_2_75', 'adult_2_76', 'adult_2_77', 'adult_2_78', 'adult_2_79', 'adult_2_80', 'adult_2_81', 'adult_2_82', 'adult_2_83', 'adult_2_84', 'adult_2_85', 'adult_2_86', 'adultparalysis1', 'adultparalysis2', 'adultparalysis3', 'adultparalysis4', 'adultparalysis5', 'adultparalysis6', 'adultparalysis7', 'adultparalysis8', 'adultparalysis9', 'adultparalysis10', 'adult_2_87a', 'adult_3_1', 'adult_3_2', 'adult_3_3', 'adult_3_4', 'adult_3_5', 'adult_3_6', 'adult_3_7', 'adult_3_8', 'adult_3_8a', 'adult_3_9', 'adult_3_10', 'adult_3_11', 'adult_3_11a', 'adult_3_12', 'adult_3_13', 'adult_3_14', 'adult_3_15', 'adult_3_16', 'adult_3_16a', 'adult_3_17', 'adult_3_18', 'adult_3_19', 'adult_3_20', 'adult_4_1', 'adult_4_2', 'adult_4_2a', 'adult_4_3a', 'adult_4_4a', 'adult_4_5', 'adult_4_6', 'adultinjury1', 'adultinjury2', 'adultinjury3', 'adultinjury4', 'adultinjury5', 'adultinjury6', 'adultinjury7', 'adultinjury8', 'adult_5_2a', 'adult_5_3', 'adult_5_4', 'adult_5_5', 'adult_6_1', 'adult_6_3', 'adult_6_4', 'adult_6_5', 'adult_6_6d', 'adult_6_6c', 'adult_6_6b', 'adult_6_6h', 'adult_6_6g', 'adult_6_6f', 'adult_6_7c', 'adult_6_7b', 'adult_6_7a', 'adult_6_8', 'adult_6_9', 'adult_6_10', 'adult_6_11', 'adult_6_12', 'adult_6_13', 'adult_6_14', 'adult_6_15', 'a7_01', 'a7_02', 'a7_03', 'child_1_1', 'child_1_2', 'child_1_3', 'child_1_4', 'child_1_5', 'child_1_6', 'child_1_6a', 'child_1_7', 'child_1_8', 'child_1_8a', 'child_1_11', 'child_1_12', 'child_1_13', 'child_1_14', 'child_1_15', 'child_1_16', 'child_1_17', 'child_1_18', 'childabnorm1', 'childabnorm2', 'childabnorm3', 'childabnorm4', 'child119a', 'childabnorm5', 'child_1_20', 'child_1_21', 'child_1_22', 'child_1_22a', 'child_1_23', 'complications1', 'complications2', 'complications3', 'complications4', 'complications5', 'complications6', 'complications7', 'complications8', 'complications9', 'complications10', 'complications11', 'complications12', 'child_2_2', 'child_2_2a', 'child_2_3', 'child_2_4', 'child_2_5', 'child_2_6', 'child_2_7', 'child_2_8', 'child_2_8a', 'child_2_9', 'child_2_10', 'child_2_10a', 'child_2_11', 'child_2_12', 'child_2_15', 'child_2_15a', 'child_2_17', 'child_2_18', 'child_3_1', 'child_3_2', 'childabnorm31', 'childabnorm32', 'childabnorm33', 'childabnorm34', 'child_3_3a', 'childabnorm35', 'child_3_4', 'child_3_5', 'child_3_6', 'child_3_7', 'child_3_8', 'child_3_9', 'child_3_10', 'child_3_11', 'child_3_12', 'child_3_13', 'child_3_14', 'child_3_14a', 'child_3_15', 'child_3_16', 'child_3_17', 'child_3_18', 'child_3_18a', 'child_3_19', 'child_3_19a', 'child_3_20', 'child_3_21', 'child_3_21a', 'child_3_22', 'child_3_22a', 'child_3_23', 'child_3_24', 'child_3_25', 'child_3_26', 'child_3_27', 'child_3_27a', 'child_3_28', 'child_3_28a', 'child_3_29', 'child_3_30', 'child_3_30a', 'child_3_31', 'child_3_31a', 'child_3_32', 'child_3_33', 'child_3_34', 'child_3_35', 'child_3_36', 'child_3_37', 'child_3_38', 'child_3_39', 'child_3_40', 'child_3_41', 'child_3_42', 'child_3_43', 'child_3_44', 'child_3_45', 'child_3_45a', 'child_3_46', 'child_3_47', 'child_3_48', 'child_3_49', 'child_4_1', 'child_4_2', 'child_4_2a', 'child_4_3', 'child_4_4', 'child_4_5', 'child_4_6', 'child_4_7', 'child_4_7a', 'child_4_8', 'child_4_8a', 'child_4_9', 'child_4_10', 'child_4_10a', 'child_4_11', 'child_4_12', 'child_4_13', 'child_4_13a', 'child_4_14', 'child_4_15', 'child_4_16', 'child_4_17', 'child_4_17a', 'child_4_18', 'child_4_19', 'child_4_19a', 'child_4_20', 'child_4_22', 'child_4_23', 'child_4_24', 'child_4_25', 'child_4_26', 'child_4_27', 'child_4_28', 'child_4_29', 'child_4_30', 'child_4_31', 'child_4_32', 'child_4_33', 'child_4_33a', 'child_4_34', 'child_4_35', 'child_4_36', 'child_4_37', 'child_4_38', 'child_4_39', 'child_4_40', 'child_4_41', 'child_4_42', 'child_4_43', 'child_4_44', 'child_4_45', 'child_4_46', 'childinjury1', 'childinjury2', 'childinjury3', 'childinjury4', 'childinjury5', 'childinjury6', 'childinjury7', 'childinjury8', 'child_4_48a', 'childinjury10', 'childinjury9', 'child_4_49', 'child_4_50', 'child_5_1', 'provider1', 'provider2', 'provider3', 'provider4', 'provider5', 'provider6', 'provider7', 'provider8', 'provider9', 'provider10', 'provider11', 'provider12', 'provider13', 'provider14', 'child_5_3', 'child_5_4', 'child_5_5', 'child_5_6d', 'child_5_6c', 'child_5_6b', 'child_5_7d', 'child_5_7c', 'child_5_7b', 'child_5_6e', 'child_5_6f', 'child_5_7e', 'child_5_7f', 'child_5_8c', 'child_5_8b', 'child_5_8a', 'child_5_9', 'child_5_10', 'child_5_11', 'child_5_12', 'child_5_13', 'child_5_14', 'child_5_15', 'child_5_16', 'child_5_17', 'child_5_18', 'child_5_19', 'c6_01', 'c6_02', 'c6_03', 'adult_4_2', 'adult_5_1', 'adult_6_2', 'child_4_47']
        # 
        #       
        #  # make a list of columns to drop because we don't need them for processing
        #  droplist = list()
        #          
        #  for word in headers:
        #      if word not in keepColumns:
        #          index = headers.index(word)
        #          droplist.append(index)
        #  
        #  #reverse the list so as to not screw up indexes as we drop things
        #  droplist.sort(reverse=True)
        #  for dropindex in droplist:
        #      # remove the header
        #      del headers[dropindex]
        #      # then remove the corresponding value in all of our rows
        #      for row in matrix:
        #          del row[dropindex]
        
        updatestr = "Text substitution\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        wordSubs = {'abdomin':'abdomen', 'abdominal':'abdomen', 'accidentally':'accident', 'accidently':'accident', 'accidental':'accident', 'accidently':'accident', 'acute myocardial infarction':'ami', 'aids':'hiv', 'anaemia':'anemia', 'anemic':'anemia', 'baby\'s':'babi', 'babies':'babi', 'baby':'babi', 'bit':'bite', 'bitten':'bite', 'bleed':'blood', 'bleeding':'blood', 'blood pressure':'hypertension', 'burn':'fire', 'burns':'fire', 'burnt':'fire', 'burned':'fire', 'burning':'fire', 'burnings':'fire', 'c section':'csection', 'caesarean':'cesarean', 'caesarian':'cesarean', 'cancerous':'cancer', 'carcinoma':'cancer', 'cardiac':'cardio', 'cardiogenic':'cardio', 'cerebrovascular':'cerebral', 'cervical':'cervix', 'cesarian':'cesarean', 'comatose':'coma', 'convulsions':'convulsion', 'death':'dead', 'dehydrated':'dehydrate', 'dehydration':'dehydrate', 'delivered':'deliver', 'deliveries':'deliver', 'delivery':'deliver', 'diarrheal':'diarrhea', 'difficult breath':'dyspnea', 'difficult breathing':'dyspnea', 'difficulty ':'difficult', 'digestion':'digest', 'digestive':'digest', 'dog bite':'dogbite', 'drank':'drink', 'drawn':'drown', 'drowned':'drown', 'drowning':'drown', 'drunk':'drink', 'dysentary':'diarrhea', 'dyspneic':'dyspnea', 'eclaupsia':'eclampsia', 'edemata':'edema', 'edematous':'edema', 'edoema':'edema', 'ekg':'ecg', 'esophageal':'esophag', 'esophagus':'esophag', 'fallen':'fall', 'falling':'fall', 'feet':'foot', 'fell':'fall', 'heart attack':'ami', 'herniation':'hernia', 'hypertensive':'hypertension', 'incubator':'incubate', 'infected':'infect', 'infectious':'infect', 'injured':'injury', 'injured':'injury', 'injures':'injury', 'injuries':'injury', 'ischemic':'ischemia', 'labour':'labor', 'maternity':'maternal', 'msb':'stillbirth', 'oxygenated':'oxygen', 'paralysis':'paralyze', 'poisoning':'poison', 'poisonous':'poison', 'pregnant':'pregnancy', 'premature':'preterm', 'prematurity':'preterm', 'septic':'sepsis', 'septicaemia':'septicemia', 'septicaemia':'sepsis', 'septicemia':'sepsis', 'smoker':'smoke', 'stroked':'stroke', 'swollen':'swell', 'tb':'tb', 't.b':'tb', 't.b.':'tb', 'transfussed':'transfuse', 'transfussion':'transfuse', 'tuberculosis':'tb', 'urinary':'urine', 'venomous':'venom', 'violent':'violence', 'vomits':'vomit', 'vomitting':'vomit', 'yellowish':'yellow'}
        
        freeText = ['adult_5_2a', 'adult_6_8',  'adult_6_11', 'adult_6_12', 'adult_6_13', 'adult_6_14', 'adult_6_15', 'a7_01', 'a7_02', 'a7_03', 'child_5_9',  'child_5_12', 'child_5_13', 'child_5_14', 'child_5_15', 'child_5_16', 'c6_01', 'c6_02', 'c6_03']
        
        # this just does a substituion of words in the above list (mostly misspellings, etc..)
        for question in freeText:
            index = headers.index(question)
            for row in matrix:
                answer = row[index]
                newanswer = answer.lower()
                # check to see if any of the keys exist in the freetext
                for key in wordSubs.keys():
                    if key in newanswer:
                        # if it exists, replace it with the word(s) from the dictionary
                        newanswer = string.replace(newanswer, key, wordSubs[key])
                row[index] = newanswer
        
        updatestr = "Writing adult, child, neonate prepped.csv files\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
        # write out header files
        adultwriter.writerow(headers)
        childwriter.writerow(headers)
        neonatewriter.writerow(headers)
        
        # write out data by row into appropriate age range (adult, child, neonate)
        for a in matrix:
            ageindex = headers.index("gen_5_4a")
            age = int(a[ageindex])
            if age >= 12:
                adultwriter.writerow(a)
            else:
                days = int(a[headers.index("gen_5_4c")])
                months = int(a[headers.index("gen_5_4b")])
                if days <= 28 and months == 0 and age == 0:
                    neonatewriter.writerow(a)
                else:
                    childwriter.writerow(a)
               
        return 1
    	
        
        