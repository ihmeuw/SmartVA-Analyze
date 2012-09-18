import csv
import workerthread
import wx

# TEST STUFF

#things we acept for neonate
acceptable_inputs = {'g1_01d', 'g1_01m', 'g1_01y', 'g1_05', 'g1_06d', 'g1_06m', 'g1_06y', 'g1_07a', 'g1_07b', 'g1_07c', 'g1_08', 'g1_09', 'g1_10', 'g2_01', 'g2_02', 
'g2_03ad', 'g2_03am', 'g2_03ay', 'g2_03bd', 'g2_03bm', 'g2_03by', 'g2_03cd', 'g2_03cm', 'g2_03cy', 'g2_03dd', 'g2_03dm', 'g2_03dy', 'g2_03ed', 'g2_03em', 'g2_03ey', 
'g2_03fd', 'g2_03fm', 'g2_03fy', 'g3_01', 'g4_02', 'g4_03a', 'g4_03b', 'g4_04', 'g4_05', 'g4_06', 'g4_07', 'g4_08', 'g5_01d', 'g5_01m', 'g5_01y', 'g5_03d', 'g5_03m', 
'g5_03y', 'g5_05', 'g5_06a', 'g5_06b', 'g5_07', 'g5_08', 'g5_04a', 'g5_04b', 'g5_04c', 'c1_01', 'c1_02', 'c1_03', 'c1_04', 'c1_05b', 'c1_06a', 'c1_07', 'c1_08b', 'c1_09', 
'c1_11', 'c1_12', 'c1_13', 'c1_14', 'c1_15', 'c1_16', 'c1_17', 'c1_18', 'c1_19_1', 'c1_19_2', 'c1_19_3', 'c1_19_4a', 'c1_20b', 'c1_21b', 'c1_22a', 'c1_25', 'c1_26', 
'c2_01_1', 'c2_01_2', 'c2_01_3', 'c2_01_4', 'c2_01_5', 'c2_01_6', 'c2_01_7', 'c2_01_8', 'c2_01_9', 'c2_01_10', 'c2_01_12', 'c2_01_14', 'c2_02b', 'c2_03', 'c2_04', 
'c2_05b', 'c2_06', 'c2_07', 'c2_08a', 'c2_09', 'c2_10b', 'c2_11', 'c2_12', 'c2_13a', 'c2_15a', 'c2_17', 'c2_18', 'c3_01', 'c3_02', 'c3_03_1', 'c3_03_2', 'c3_03_3', 
'c3_04', 'c3_05', 'c3_06', 'c3_07', 'c3_08', 'c3_09', 'c3_10', 'c3_11', 'c3_12', 'c3_13', 'c3_14b', 'c3_15', 'c3_16', 'c3_17', 'c3_18b', 'c3_19b', 'c3_20', 'c3_21b', 
'c3_22b', 'c3_23', 'c3_24', 'c3_25', 'c3_26', 'c3_27b', 'c3_28b', 'c3_29', 'c3_30b', 'c3_31b', 'c3_32', 'c3_33', 'c3_34', 'c3_35', 'c3_36', 'c3_37', 'c3_38', 'c3_39', 
'c3_40', 'c3_41', 'c3_42', 'c3_44', 'c3_45b', 'c3_46', 'c3_47', 'c3_48', 'c3_49', 'c4_01', 'c4_02b', 'c4_03', 'c4_04', 'c4_05', 'c4_06', 'c4_07b', 'c4_08b', 'c4_09', 
'c4_10b', 'c4_11', 'c4_12', 'c4_13b', 'c4_14', 'c4_15', 'c4_16', 'c4_17b', 'c4_18', 'c4_19b', 'c4_20', 'c4_22', 'c4_23', 'c4_24', 'c4_25', 'c4_26', 'c4_27', 'c4_28', 
'c4_29', 'c4_30', 'c4_31_1', 'c4_31_2', 'c4_32', 'c4_33b', 'c4_34', 'c4_35', 'c4_36', 'c4_37b', 'c4_38', 'c4_39', 'c4_40', 'c4_41', 'c4_42', 'c4_43', 'c4_44', 'c4_46', 
'c4_47_1', 'c4_47_2', 'c4_47_3', 'c4_47_4', 'c4_47_5', 'c4_47_6', 'c4_47_7', 'c4_47_8a', 'c4_47_9', 'c4_47_11', 'c4_48', 'c4_49b', 'c5_01', 'c5_02_1', 'c5_02_2', 
'c5_02_3', 'c5_02_4', 'c5_02_5', 'c5_02_6', 'c5_02_7', 'c5_02_8', 'c5_02_9', 'c5_02_10', 'c5_02_11a', 'c5_02_12', 'c5_07_1', 'c5_07_2', 'c5_09', 'c5_12', 'c5_13', 
'c5_14', 'c5_15', 'c5_16', 'c5_17', 'c5_18', 'c5_19', 'g5_02', 'c1_05', 'c1_20', 'c1_21', 'c2_02', 'c2_05', 'c2_10', 'c3_14', 'c3_18', 'c3_19', 'c3_21', 'c3_22', 'c3_27', 
'c3_28', 'c3_30', 'c3_31', 'c1_06b', 'c1_08a', 'c1_10', 'c1_19', 'c2_01_11', 'c2_01_13', 'c3_03_4a', 'c3_03_4b', 'c3_03_5', 'c3_03_6', 'c3_43', 'c3_45a', 'c5_02_11b', 
'c5_02_13', 'c5_02_14', 'c5_03', 'c5_04', 'c5_05', 'c5_06_1d', 'c5_06_1m', 'c5_06_1y', 'c5_06_2d', 'c5_06_2m', 'c5_06_2y', 'c5_08d', 'c5_08m', 'c5_08y', 'c5_10', 'c5_11', 
'c6_01', 'c6_02', 'c6_03', 'c6_04', 'c6_05', 'c6_06', 'c6_07', 'c6_08', 'c6_09', 'c6_10', 'c1_22b', 'c1_23', 'c1_24', 'c1_24d', 'c1_24m', 'c1_24y', 'module', 'c2_08b', 
'c2_13b', 'c2_14', 'c2_15b'}


#conversions from codebook to algorithm
replacements = {'g5_04a': 's2', 'g5_04b': 's3', 'g5_04c': 's4', 'c1_01': 's5', 'c1_02': 's6', 'c1_03': 's7', 'c1_04': 's8', 'c1_05b': 's10', 'c1_06a': 's11', 
'c1_07': 's13', 'c1_08b': 's14', 'c1_09': 's15', 'c1_11': 's16', 'c1_12': 's17', 'c1_13': 's18', 'c1_14': 's19', 'c1_15': 's20', 'c1_16': 's21', 'c1_17': 's22', 
'c1_18': 's23', 'c1_19_1': 's24', 'c1_19_2': 's25', 'c1_19_3': 's26', 'c1_19_4a': 's27', 'c1_20b': 's28', 'c1_21b': 's29', 'c1_22a': 's30', 'c1_25': 's31', 
'c1_26': 's32', 'c2_01_1': 's33', 'c2_01_2': 's34', 'c2_01_3': 's35', 'c2_01_4': 's36', 'c2_01_5': 's37', 'c2_01_6': 's38', 'c2_01_7': 's39', 'c2_01_8': 's40', 
'c2_01_9': 's41', 'c2_01_10': 's42', 'c2_01_12': 's43', 'c2_02b': 's45', 'c2_03': 's46', 'c2_04': 's47', 'c2_05b': 's48', 'c2_06': 's49', 'c2_07': 's50', 'c2_08a': 's51', 
'c2_09': 's52', 'c2_10b': 's53', 'c2_11': 's54', 'c2_12': 's55', 'c2_13a': 's56', 'c2_15a': 's57}', 'c2_17': 's58', 'c2_18': 's59', 'c3_01': 's60', 'c3_02': 's61', 
'c3_03_1': 's62', 'c3_03_2': 's63', 'c3_03_3': 's64', 'c3_04': 's65', 'c3_05': 's66', 'c3_06': 's67', 'c3_07': 's68', 'c3_08': 's69', 'c3_09': 's70', 'c3_10': 's71', 
'c3_11': 's72', 'c3_12': 's73', 'c3_13': 's74', 'c3_14b': 's75', 'c3_15': 's76', 'c3_16': 's77', 'c3_17': 's78', 'c3_18b': 's79', 'c3_19b': 's80', 'c3_20': 's81', 
'c3_21b': 's82', 'c3_22b': 's83', 'c3_23': 's84', 'c3_24': 's85', 'c3_25': 's86', 'c3_26': 's87', 'c3_27b': 's88', 'c3_28b': 's89', 'c3_29': 's90', 'c3_30b': 's91', 
'c3_31b': 's92', 'c3_32': 's93', 'c3_33': 's94', 'c3_34': 's95', 'c3_35': 's96', 'c3_36': 's97', 'c3_37': 's98', 'c3_38': 's99', 'c3_39': 's100', 'c3_40': 's101', 
'c3_41': 's102', 'c3_42': 's103', 'c3_44': 's104', 'c3_45b': 's105', 'c3_46': 's106', 'c3_47': 's107', 'c3_48': 's108', 'c3_49': 's109', 'c4_01': 's110', 'c4_02b': 's111', 
'c4_03': 's112', 'c4_04': 's113', 'c4_05': 's114', 'c4_06': 's115', 'c4_07b': 's116', 'c4_08b': 's117', 'c4_09': 's118', 'c4_10b': 's119', 'c4_11': 's120', 'c4_12': 's121', 
'c4_13b': 's122', 'c4_14': 's123', 'c4_15': 's124', 'c4_16': 's125', 'c4_17b': 's126', 'c4_18': 's127', 'c4_19b': 's128', 'c4_20': 's129', 'c4_22': 's130', 'c4_23': 's131', 
'c4_24': 's132', 'c4_25': 's133', 'c4_26': 's134', 'c4_27': 's135', 'c4_28': 's136', 'c4_29': 's137', 'c4_30': 's138', 'c4_31_1': 's139', 'c4_31_2': 's140', 'c4_32': 's141', 
'c4_33b': 's142', 'c4_34': 's143', 'c4_35': 's144', 'c4_36': 's145', 'c4_37b': 's146', 'c4_38': 's147', 'c4_39': 's148', 'c4_40': 's149', 'c4_41': 's150', 'c4_42': 's151', 
'c4_43': 's152', 'c4_44': 's153', 'c4_46': 's154', 'c4_47_1': 's155', 'c4_47_2': 's156', 'c4_47_3': 's157', 'c4_47_4': 's158', 'c4_47_5': 's159', 'c4_47_6': 's160', 
'c4_47_7': 's161', 'c4_47_8a': 's162', 'c4_47_9': 's163', 'c4_47_11': 's164', 'c4_48': 's165', 'c4_49b': 's166', 'c5_01': 's167', 'c5_02_1': 's168', 'c5_02_2': 's169', 
'c5_02_3': 's170', 'c5_02_4': 's171', 'c5_02_5': 's172', 'c5_02_6': 's173', 'c5_02_7': 's174', 'c5_02_8': 's175', 'c5_02_9': 's176', 'c5_02_10': 's177', 'c5_02_11a': 's178', 
'c5_02_12': 's179', 'c5_07_1': 's180', 'c5_07_2': 's181', 'c5_09': 's182', 'c5_12': 's183', 'c5_13': 's184', 'c5_14': 's185', 'c5_15': 's186', 'c5_16': 's187', 'c5_17': 's188', 
'c5_18': 's189', 'c5_19': 's190', 'g5_02': 'sex', 'c1_05': 's9', 'c1_20': 's28', 'c1_21': 's29', 'c2_02': 's45', 'c2_05': 's48', 'c2_10': 's53', 'c3_14': 's75', 'c3_18': 's79', 
'c3_19': 's80', 'c3_21': 's82', 'c3_22': 's83', 'c3_27': 's88', 'c3_28': 's89', 'c3_30': 's91', 'c3_31': 's92'}
 



def validate(notify_window, inputfile):
    spamReader = csv.reader(open(inputfile, 'rbU'))
    
    firstrow =  spamReader.next()
    temp = len(firstrow)
    
    print "just curious " + str(temp)
    
    for column in firstrow:
        success = True
        if column not in acceptable_inputs:
            updatestr = "error: '" + column + "' is not a recognized column\n"
            wx.PostEvent(notify_window, workerthread.ResultEvent(updatestr))
            success = False
        else:
            test = replacements[column]
            print "woohoo " + test
            #yay, do nothing
    
    return success
    
    
    
    
    
    
# use this stuff below... the above is just a trial

import csv

#todo: are these the same as neonate?
child_skip = ['g1_01d', 'g1_01m', 'g1_01y', 'g1_05', 'g1_06d', 'g1_06m', 'g1_06y', 'g1_07a', 'g1_07b', 'g1_07c', 'g1_08', 'g1_09', 'g1_10', 'g2_01', 'g2_02', 'g2_03ad', 'g2_03am', 'g2_03ay', 'g2_03bd', 'g2_03bm', 'g2_03by', 'g2_03cd', 'g2_03cm', 'g2_03cy', 'g2_03dd', 'g2_03dm', 'g2_03dy', 'g2_03ed', 'g2_03em', 'g2_03ey', 'g2_03fd', 'g2_03fm', 'g2_03fy', 'g3_01', 'g4_02', 'g4_03a', 'g4_03b', 'g4_04', 'g4_05', 'g4_06', 'g4_07', 'g4_08', 'g5_01d', 'g5_01m', 'g5_01y', 'g5_03d', 'g5_03m', 'g5_03y', 'g5_05', 'g5_06a', 'g5_06b', 'g5_07', 'g5_08']

#updated
child_acceptible = {'c4_01' : [0, 1, 8, 9], 'c4_02a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_03' : [0, 1, 8, 9], 'c4_04' : [1, 2, 3, 8, 9], 'c4_05' : [1, 2, 3, 8, 9], 'c4_06' : [0, 1, 8, 9], 'c4_08a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_09' : [0, 1, 8, 9], 'c4_10a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c1_06' : [1, 2, 3, 4, 5, 8, 9], 'c4_11' : [0, 1, 8, 9], 'c4_12' : [0, 1, 8, 9], 'c4_13a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_14' : [0, 1, 8, 9], 'c4_15' : [0, 1, 8, 9], 'c4_16' : [0, 1, 8, 9], 'c4_17a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_18' : [0, 1, 8, 9], 'c4_19a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_20' : [0, 1, 8, 9], 'c4_22' : [0, 1, 8, 9], 'c4_23' : [0, 1, 8, 9], 'c4_24' : [0, 1, 8, 9], 'c4_25' : [0, 1, 8, 9], 'c4_26' : [0, 1, 8, 9], 'c4_27' : [1, 2, 3, 8, 9], 'c4_28' : [0, 1, 8, 9], 'c4_29' : [0, 1, 8, 9], 'c4_30' : [0, 1, 8, 9], 'c1_07' : [1, 2, 3, 4, 8, 9], 'c4_31' : [1, 2, 3, 4, 5, 8 ,9], 'c4_32' : [1, 2, 3, 4, 5, 8, 9], 'c4_33a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_34' : [0, 1, 8, 9], 'c4_35' : [0, 1, 8, 9], 'c4_36' : [0, 1, 8, 9], 'c4_37a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c4_38' : [0, 1, 8, 9], 'c4_39' : [0, 1, 8, 9], 'c4_40' : [0, 1, 8, 9], 'c4_41' : [0, 1, 8, 9], 'c4_42' : [0, 1, 8, 9], 'c4_43' : [0, 1, 8, 9], 'c4_44' : [0, 1, 8, 9], 'c4_46' : [0, 1, 8, 9], 'c4_47_1' : [0, 1, 8, 9], 'c4_47_2' : [0, 1, 8, 9], 'c4_47_3' : [0, 1, 8, 9], 'c4_47_4' : [0, 1, 8, 9], 'c4_47_5' : [0, 1, 8, 9], 'c4_47_6' : [0, 1, 8, 9], 'c4_47_7' : [0, 1, 8, 9], 'c4_47_8a' : [0, 1, 8, 9], 'c4_47_9' : [0, 1, 8, 9], 'c4_47_11' : [0, 1, 8, 9], 'c4_48' : [0, 1, 8, 9], 'c1_11' : [1, 2, 8, 9], 'c1_12' : [0, 1, 8, 9], 'c1_13' : [0, 1, 8, 9], 'c5_17' : [0, 1, 8, 9], 'c5_18' : [0, 1, 8, 9], 'c1_14' : [0, 1, 8, 9], 'c5_19' : [0, 1, 8, 9], 'c1_20a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c1_21a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c1_22a' : [1, 2, 3, 4, 5, 8, 9], 'c1_25a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c1_01' : [1, 2, 8, 9], 'c1_02' : [1, 2, 3, 8 ,9], 'c1_03' : [0, 1, 8, 9], 'c1_02' : [1, 2, 3, 8 ,9], 'c1_04' : [1, 2, 8, 9], 'c1_05a' : [1, 2, 3, 4, 5, 6, 8, 9]}

#updated
child_variables = ['g5_04', 'c4_01', 'c4_02a', 'c4_03', 'c4_04', 'c4_05', 'c4_06', 'c4_07', 'c4_08a', 'c4_09', 'c4_10a', 'c1_06', 'c4_11', 'c4_12', 'c4_13a', 'c4_14', 'c4_15', 'c4_16', 'c4_17a', 'c4_18', 'c4_19a', 'c4_20', 'c4_22', 'c4_23', 'c4_24', 'c4_25', 'c4_26', 'c4_27', 'c4_28', 'c4_29', 'c4_30', 'c1_07', 'c4_31', 'c1_08a', 'c4_32', 'c4_33a', 'c4_34', 'c4_35', 'c4_36', 'c4_37a', 'c4_38', 'c4_39', 'c4_40', 'c4_41', 'c4_42', 'c4_43', 'c4_44', 'c4_46', 'c4_47_1', 'c4_47_2', 'c4_47_3', 'c4_47_4', 'c4_47_5', 'c4_47_6', 'c4_47_7', 'c4_47_8a', 'c4_47_9', 'c4_47_11', 'c4_48', 'c1_11', 'c1_12', 'c1_13', 'c5_07_1', 'c5_07_2', 'c5_17', 'c5_18', 'c1_14', 'c5_19', 'c1_20a', 'c1_21a', 'c1_22a', 'c1_25a', 'c1_01', 'c1_02', 'c1_03', 'c1_02', 'c1_04', 'c1_05a', 'c5_09', 'c5_12', 'c5_13', 'c5_14', 'c5_15', 'c5_16', 'c6_01', 'c6_02', 'c6_03', 'c6_04', 'c6_05', 'c6_06', 'c6_07', 'c6_08', 'c6_09', 'c6_10', 'g5_02']

#no
binary_inputs = ["c1_03", "c1_12", "c1_13", "c1_14", "c1_15", "c1_16", "c1_17", "c1_18", "c1_19_1", "c1_19_2", "c1_19_3", "c1_19_4a", "c1_26", "c2_01_1", "c2_01_2", "c2_01_3", "c2_01_4", "c2_01_5", "c2_01_6", "c2_01_7", "c2_01_8", "c2_01_9", "c2_01_10", "c2_01_12", "c2_04", "c2_09", "c2_11", "c2_18", "c3_01", "c3_02", "c3_03_1", "c3_03_2", "c3_03_3", "c3_04", "c3_05", "c3_06", "c3_07", "c3_09", "c3_11", "c3_12", "c3_13", "c3_16", "c3_17", "c3_20", "c3_23", "c3_24", "c3_25", "c3_26", "c3_29", "c3_32", "c3_33", "c3_34", "c3_35", "c3_36", "c3_37", "c3_38", "c3_39", "c3_40", "c3_41", "c3_42", "c3_44", "c3_46", "c3_47", "c3_48", "c3_49"]

#updated
svars = ['s110', 's111', 's112', 's113991', 's114991', 's115', 's116991', 's117', 's118', 's119', 's11991', 's120', 's121', 's122', 's123', 's124', 's125', 's126', 's127', 's128', 's129', 's130', 's131', 's132', 's133', 's134', 's135991', 's136', 's137', 's138', 's13991', 's139991', 's14', 's141991', 's142', 's143', 's144', 's145', 's146', 's147', 's148', 's149', 's150', 's151', 's152', 's153', 's154', 's155', 's156', 's157', 's158', 's159', 's160', 's161', 's162', 's163', 's164', 's165', 's16991', 's17', 's18', 's180', 's181', 's188', 's189', 's19', 's190', 's28', 's29', 's30991', 's31', 's5991', 's6991', 's7', 's8991', 's8992', 's9', 's99991', 's999910', 's999911', 's999912', 's999913', 's999914', 's999915', 's999916', 's999917', 's999918', 's999919', 's99992', 's999920', 's999921', 's999922', 's999923', 's999924', 's999925', 's999926', 's999927', 's999928', 's999929', 's99993', 's999930', 's999931', 's999932', 's999933', 's999934', 's999935', 's999936', 's999937', 's999938', 's999939', 's99994', 's999940', 's999941', 's999942', 's999943', 's999944', 's999945', 's999946', 's999947', 's999948', 's999949', 's99995', 's999950', 's999951', 's999952', 's999953', 's999954', 's999955', 's999956', 's999957', 's999958', 's999959', 's99996', 's999960', 's999961', 's999962', 's999963', 's999964', 's999965', 's999966', 's999967', 's999968', 's999969', 's99997', 's999970', 's999971', 's999972', 's999973', 's999974', 's999975', 's99998', 's99999']

#updated
text_columns = ['c5_09', 'c5_12', 'c5_13', 'c5_14', 'c5_15', 'c5_16', 'c6_01', 'c6_02', 'c6_03', 'c6_04', 'c6_05', 'c6_06', 'c6_07', 'c6_08', 'c6_09', 'c6_10']

def zero(arrayVar):
    tempDict = {}
    for val in arrayVar:
        tempDict[val] = 0
    return tempDict

# for bianry inputs
def myfun(column):
    if column_headers[col_i] in binary_inputs:
        if column != 1:
            return 0
        else:
            return 1

# algorithm for finding bad inputs
def a():
    inputfile = "/Users/carlhartung/Desktop/testing.csv"
    spamReader = csv.reader(open(inputfile, 'rbU'))
    
    column_headers = {}
    skip = []
    for (index, row) in enumerate(spamReader):
        if (index == 0):
            # first row is headers
            for (col_i, column) in enumerate(row):
                if not(column in child_variables or column in child_skip):
                    #print column in neonate_map
                    #print column in neonate_skip
                    print 'warning: ' + column + " unknown. Proceeding without using this column"
                    # for now just skip unknown column headers.. later this should be an error
                    skip.append(col_i)
                else:
                    # print 'replacing with ' + neonate_map[column]
                    
                    # build a map of {index, header}
                    column_headers.update({col_i : column})
        else:
            soutput = zero(svars)
            for (col_i, column) in enumerate(row):
                if col_i in skip:
                    continue
                #print 'testing ' + column_headers[col_i]
                if (column_headers[col_i] in text_columns):
                    print column_headers[col_i] + "is a text column"
                    continue
                #print "testing " + column + " in " + column_headers[col_i] + " output is: " + str(neo_acceptible[column_headers[col_i]])
                #print int(column) in neo_acceptible[column_headers[col_i]]
                if column is None or column is '':
                    continue
                if not(int(column) in neo_acceptible[column_headers[col_i]]):
                    print "Error in Row " + str(index) + " Column " + str(col_i) + ": " + column + " is not an acceptible answer for " + column_headers[col_i] + ". Acceptible answers are: " + str(neo_acceptible[column_headers[col_i]])
                
                print 'transposing '  + column_headers[col_i] + ' with val ' + str(column)
                #transpose = fmap[column_headers[col_i]](column)
                transpose = fmap.get(column_headers[col_i], b)(column)
                print transpose
                if transpose is not None:
                    for key, value in transpose.iteritems():
                        print "trying " + key + ", " + str(value)
                        if value == 9999:
                            del soutput[key]
                        else:
                            soutput[key] = value
                #print "done loop"
            #for key, value in soutput.it:
            #    print key + ", " + str(value)
            print soutput
            
#algorithm for converting inputs
def b():
    print 'woot'
    
                
    # once we've verified everything, go ahead and write the new s column headers to a file, along with all the data
    

algorithm(inputfile = "/Users/carlhartung/Desktop/SmartVA/Examples/NeonateuniformTrain-new.csv")


#updated for child
# The following methods convert the "c" variables into "s" variables with their appropriate values.
# The "s" values already start at zero, so these only need to change them to 1 if appropriate


def c4_01(value):
    if int(value) == 1:
        return {'s110' : 1}

def c4_03(value):
    if int(value) == 1:
        return {'s112': 1}

def c4_04(value):
    if int(value) == 3:
        return {'s113991', 1}

def c4_05(value):
    if int(value) == 2 or int(value) == 23:
        return {'s114991', 1}

def c4_06(value):
    if int(value) == 1:
        return {'s115': 1}

def c4_07(value):
    if int(value) > 2:
        return {'s116991': 1}

def c4_09(value):
    if int(value) == 1:
        return {'s118': 1}     

def c1_06(value):
    if int(value) == 4 or int(value) == 5:
           return {'s11991': 1}
           
def c4_11(value):
    if int(value) == 1:
        return {'s120': value}           

def c4_12(value):
    if int(value) == 1:
        return {'s121': value}           

def c4_13a(value):
    if int(value) == 1:
        return {'s122': value}               

def c4_14(value):
    if int(value) == 1:
        return {'s123': value}               

def c4_15(value):
    if int(value) == 1:
        return {'s124': value}               

def c4_16(value):
    if int(value) == 1:
        return {'s125': value}               

def c4_17(value):
    if int(value) == 1:
        return {'s126': value}           

def c4_18(value):
    if int(value) == 1: 
        return {'s127': value}           

def c4_19a(value):
    if int(value) == 1:
        return {'s128': value}               

def c4_20(value):
    if int(value) == 1:
        return {'s129': value}               

def c4_22(value):
    if int(value) == 1:
        return {'s130': value}               

def c4_23(value):
    if int(value) == 1:
           return {'s131': 1}

def c4_24(value):
    if int(value) == 1:
        return {'s132': 1}

def c4_25(value):
    if int(value) == 1:
        return {'s133': 1}           

def c4_26(value):
    if int(value) == 1:
        return {'s134': 1}           

def c4_27(value):
    if int(value) == 3:
        return {'s135991': 1}               

def c4_28(value):
    if int(value) == 1:
        return {'s136': 1}               

def c4_29(value):
    if int(value) == 1:
        return {'s137': value}               

def c4_30(value):
    if int(value) == 1:
        return {'s138': value}               

def c1_07(value):
    if int(value) == 1 or int(value) == 2:
        return {'s13991': 1}           

def c4_31(value):
    if int(value) == 1: 
        return {'s139991': 1}           

def c4_32a(value):
    if int(value) == 1:
        return {'s141991': 1}               

def c4_34(value):
    if int(value) == 1:
        return {'s143': 1}               
 
def c4_35(value):
    if int(value) == 1:
        return {'s144': 1}         
           
def c4_36(value):
    if int(value) == 1:
      return {'s145': 1}           

def c4_38(value):
    if int(value) == 1:
      return {'s147': 1}

def c4_39(value):
    if int(value) == 1:
        return {'s148': 1}

def c4_40(value):
    if int(value) == 1:
        return {'s149': 1}

def c4_41(value):
    if int(value) == 1:
        return {'s150': 1}

def c4_42(value):
    if int(value) == 1:
        return {'s151': 1}
            
def c4_43(value):
    if int(value) == 1:
        return {'s152': 1}
    
def c4_44(value):
    if int(value) == 1:
        return {'s153': 1}  
    
def c4_46(value):
    if int(value) == 1:
        return {'s154': 1} 
    
def c4_47_1(value):
    if int(value) == 1:
        return {'s155': 1}

def c4_47_2(value):
    if int(value) == 1:
        return {'s156': 1}

def c4_47_3(value):
    if int(value) == 1:
        return {'s157': 1}

def c4_47_4(value):
    if int(value) == 1:
        return {'s158': 1}

def c4_47_5(value):
    if int(value) == 1:
        return {'s159': 1}

def c4_47_6(value):
    if int(value) == 1:
        return {'s160': 1}

def c4_47_7(value):
    if int(value) == 1:
        return {'s161': 1}

def c4_47_8a(value):
    if int(value) == 1:
        return {'s162': 1}

def c4_47_9(value):
    if int(value) == 1:
        return {'s163': 1}

def c4_47_11(value):
    if int(value) == 1:
        return {'s164': 1}

def c4_48(value):
    if int(value) == 1:
        return {'s165': 1}

def c1_11(value):
    if int(value) == 1:
        return {'s16991': 1}

def c1_12(value):
    if int(value) == 1:
        return {'s17': 1}

def c1_13(value):
    if int(value) == 1:
        return {'s18': 1}

def c5_07_1(value):
    if int(value) == 9999:
        return {'s180': 9999}
    
def c5_07_2(value):
    if int(value) == 9999:
        return {'s181': 9999}

def c5_17(value):
    if int(value) == 1:
        return {'s188': 1}

def c5_18(value):
    if int(value) == 1:
        return {'s189': 1}

def c1_14(value):
    if int(value) == 1:
        return {'s19': 1}

def c5_19(value):
    if int(value) == 2:
        return {'s190': 1}    

def c1_20a(value):
    if int(value) == 1:
        return {'s28': 1}

def c1_21a(value):
    if int(value) == 1:
        return {'s29': 1}

def c1_22a(value):
    if int(value) == 3 or int(value) == 4:
        return {'s30991': 1}

def c1_01(value):
    if int(value) == 2:
        return {'s5991': 1}

def c1_02(value):
    returndict = {}
    if int(value) == 2 or int(value) == 3:
        returndict['s6991'] = 1
    elif int(value) == 1:
        returndict['s8991'] = 1
    return returndict

def c1_03(value):
    if int(value) == 1:
        return {'s7': 1}

def c1_04(value):
    if int(value) == 2:
        return {'s8992': 1}
   
   
    
# these are all the text variables   
# updated for child
def wordsearch(value):
    returndict = {}
    if value is None:
        return {}
    if 'abdomen' in value:
          returndict['s99991'] = 1
    if 'brain' in value:
        returndict['s999910'] = 1
    if 'breath' in value:
        returndict['s999911'] = 1
    if 'cancer' in value:
        returndict['s999912'] = 1
    if 'cardio' in value:
        returndict['s999913'] = 1
    if 'chest' in value:
        returndict['s999914'] = 1
    if 'cold' in value:
        returndict['s999915'] = 1
    if 'coma' in value:
        returndict['s999916'] = 1
    if 'convuls' in value:
        returndict['s999917'] = 1
    if 'cough' in value:
        returndict['s999918'] = 1
    if 'dead' in value:
        returndict['s999919'] = 1
    if 'accid' in value:
        returndict['s99992'] = 1
    if 'dehydr' in value:
        returndict['s999920'] = 1
    if 'deliv' in value:
        returndict['s999921'] = 1
    if 'dengu' in value:
        returndict['s999922'] = 1
    if 'diarrhea' in value:
        returndict['s999923'] = 1
    if 'drink' in value:
        returndict['s999924'] = 1
    if 'drown' in value:
        returndict['s999925'] = 1
    if 'eat' in value:
        returndict['s999926'] = 1
    if 'eye' in value:
        returndict['s999927'] = 1
    if 'fall' in value:
        returndict['s999928'] = 1 
    if 'fever' in value:
        returndict['s999929'] = 1
    if 'acidosi' in value:
        returndict['s99993'] = 1
    if 'fire' in value:
        returndict['s999930'] = 1
    if 'gastric' in value:
        returndict['s999931'] = 1
    if 'glucos' in value:
        returndict['s999932'] = 1
    if 'head' in value:
        returndict['s999933'] = 1
    if 'headach' in value:
        returndict['s999934'] = 1
    if 'heart' in value:
        returndict['s999935'] = 1
    if 'hiv' in value:
        returndict['s999936'] = 1
    if 'hypertens' in value:
        returndict['s999937'] = 1
    if 'icu' in value:
        returndict['s999938'] = 1
    if 'indraw' in value:
        returndict['s999939'] = 1
    if 'anemia' in value:
        returndict['s99994'] = 1
    if 'infect' in value:
        returndict['s999940'] = 1
    if 'injuri' in value:
        returndict['s999941'] = 1  
    if 'jaundic' in value:
        returndict['s999942'] = 1
    if 'kidney' in value:
        returndict['s999943'] = 1
    if 'leukemia' in value:
        returndict['s999944'] = 1  
    if 'lung' in value:
        returndict['s999945'] = 1
    if 'malaria' in value:
        returndict['s999946'] = 1
    if 'malnutrit' in value:
        returndict['s999947'] = 1    
    if 'measl' in value:
        returndict['s999948'] = 1
    if 'neck' in value:
        returndict['s999949'] = 1
    if 'asthma' in value:
        returndict['s99995'] = 1
    if 'nose' in value:
        returndict['s999950'] = 1  
    if 'oxygen' in value:
        returndict['s999951'] = 1
    if 'pain' in value:
        returndict['s999952'] = 1
    if 'pneumonia' in value:
        returndict['s999953'] = 1
    if 'poison' in value:
        returndict['s999954'] = 1  
    if 'pox' in value:
        returndict['s999955'] = 1
    if 'pregnanc' in value:
        returndict['s999956'] = 1
    if 'pulmonari' in value:
        returndict['s999957'] = 1  
    if 'rash' in value:
        returndict['s999958'] = 1
    if 'respiratori' in value:
        returndict['s999959'] = 1
    if 'babi' in value:
        returndict['s99996'] = 1    
    if 'road' in value:
        returndict['s999960'] = 1
    if 'sepsi' in value:
        returndict['s999961'] = 1
    if 'shock' in value:
        returndict['s999962'] = 1
    if 'skin' in value:
        returndict['s999963'] = 1  
    if 'snake' in value:
        returndict['s999964'] = 1
    if 'stomach' in value:
        returndict['s999965'] = 1
    if 'stool' in value:
        returndict['s999966'] = 1
    if 'swell' in value:
        returndict['s999967'] = 1  
    if 'tetanus' in value:
        returndict['s999968'] = 1
    if 'transfus' in value:
        returndict['s999969'] = 1
    if 'bite' in value:
        returndict['s99997'] = 1  
    if 'unconsci' in value:
        returndict['s999970'] = 1
    if 'urin' in value:
        returndict['s999971'] = 1
    if 'vomit' in value:
        returndict['s999972'] = 1    
    if 'ward' in value:
        returndict['s999973'] = 1
    if 'water' in value:
        returndict['s999974'] = 1
    if 'yellow' in value:
        returndict['s999975'] = 1
    if 'blood' in value:
        returndict['s99998'] = 1  
    if 'bluish' in value:
        returndict['s9999'] = 1 


def c3_43(value):
    return wordsearch(value)

def c5_09(value):
    return wordsearch(value)

def c5_12(value):
    return wordsearch(value)

def c5_13(value):
    return wordsearch(value)
    
def c5_14(value):
    return wordsearch(value)

def c5_15(value):
    return wordsearch(value)

def c5_16(value):
    return wordsearch(value)

def c6_01(value):
    return wordsearch(value)

def c6_02(value):
    return wordsearch(value)

def c6_03(value):
    return wordsearch(value)

def c6_04(value):
    return wordsearch(value)

def c6_05(value):
    return wordsearch(value)

def c6_06(value):
    return wordsearch(value)

def c6_07(value):
    return wordsearch(value)

def c6_08(value):
    return wordsearch(value)

def c6_09(value):
    return wordsearch(value)     

def c6_10(value):
    return wordsearch(value)   



# maps strings to functions.  i.e. 'c1_01' to c1_01()
fmap = dict(c1_01=c1_01, c1_02=c1_02, c1_03=c1_03, c1_04=c1_04, c1_04=c1_04, c1_05a=c1_05a, c1_06a=c1_06a, c1_07=c1_07, c1_08b=c1_08b, c1_09=c1_09, c1_11=c1_11, c1_12=c1_12, c1_13=c1_13, c1_14=c1_14, c1_15=c1_15, c1_16=c1_16, c1_17=c1_17, c1_18=c1_18, c1_19_1=c1_19_1, c1_19_2=c1_19_2, c1_19_3=c1_19_3, c1_19_4a=c1_19_4a, c1_20a=c1_20a, c1_21a=c1_21a, c1_22a=c1_22a, c1_25a=c1_25a, c1_26=c1_26, c2_01_1=c2_01_1, c2_01_2=c2_01_2, c2_01_3=c2_01_3, c2_01_4=c2_01_4, c2_01_5=c2_01_5, c2_01_6=c2_01_6, c2_01_7=c2_01_7, c2_01_8=c2_01_8, c2_01_9=c2_01_9, c2_01_10=c2_01_10, c2_01_12=c2_01_12, c2_02a=c2_02a, c2_03=c2_03, c2_03=c2_03, c2_04=c2_04, c2_05a=c2_05a, c2_06=c2_06, c2_07=c2_07, c2_08a=c2_08a, c2_09=c2_09, c2_10a=c2_10a, c2_11=c2_11, c2_12=c2_12, c2_13a=c2_13a, c2_15a=c2_15a, c2_17=c2_17, c2_17=c2_17, c2_17=c2_17, c2_17=c2_17, c2_18=c2_18, c3_01=c3_01, c3_02=c3_02, c3_03_1=c3_03_1, c3_03_2=c3_03_2, c3_03_3=c3_03_3, c3_04=c3_04, c3_05=c3_05, c3_06=c3_06, c3_07=c3_07, c3_08=c3_08, c3_09=c3_09, c3_10=c3_10, c3_11=c3_11, c3_12=c3_12, c3_13=c3_13, c3_14a=c3_14a, c3_15=c3_15, c3_16=c3_16, c3_17=c3_17, c3_18a=c3_18a, c3_19a=c3_19a, c3_20=c3_20, c3_21a=c3_21a, c3_22a=c3_22a, c3_23=c3_23, c3_24=c3_24, c3_25=c3_25, c3_26=c3_26, c3_27a=c3_27a, c3_28a=c3_28a, c3_29=c3_29, c3_30a=c3_30a, c3_31a=c3_31a, c3_32=c3_32, c3_33=c3_33, c3_34=c3_34, c3_35=c3_35, c3_36=c3_36, c3_37=c3_37, c3_38=c3_38, c3_39=c3_39, c3_40=c3_40, c3_41=c3_41, c3_42=c3_42, c3_44=c3_44, c3_45a=c3_45a, c3_46=c3_46, c3_47=c3_47, c3_48=c3_48, c3_49=c3_49, c5_07=c5_07, c5_07=c5_07, c5_17=c5_17, c5_18=c5_18, c5_19=c5_19, c3_43=c3_43, c5_09=c5_09, c5_12=c5_12, c5_13=c5_13, c5_14=c5_14, c5_15=c5_15, c5_16=c5_16, c6_01=c6_01, c6_02=c6_02, c6_03=c6_03, c6_04=c6_04, c6_05=c6_05, c6_06=c6_06, c6_07=c6_07, c6_08=c6_08, c6_09=c6_09, c6_10=c6_10, g5_02=g5_02, g5_04=g5_04, g5_04=g5_04, g5_04=g5_04, g5_04=g5_04, c3_43=c3_43, c5_09=c5_09, c5_12=c5_12, c5_13=c5_13, c5_14=c5_14, c5_15=c5_15, c5_16=c5_16, c6_01=c6_01, c6_02=c6_02, c6_03=c6_03, c6_04=c6_04, c6_05=c6_05, c6_06=c6_06, c6_07=c6_07, c6_08=c6_08, c6_09=c6_09, c6_10=c6_10)


# def myfun(column, value):
#     if column is 'c1_01':
#         if value == 2:
#             return ['s5', 1]
#         else:
#             return ['s5', 2]
    



