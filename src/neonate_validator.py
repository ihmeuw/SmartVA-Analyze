import csv

neonate_skip = ['g1_01d', 'g1_01m', 'g1_01y', 'g1_05', 'g1_06d', 'g1_06m', 'g1_06y', 'g1_07a', 'g1_07b', 'g1_07c', 'g1_08', 'g1_09', 'g1_10', 'g2_01', 'g2_02', 'g2_03ad', 'g2_03am', 'g2_03ay', 'g2_03bd', 'g2_03bm', 'g2_03by', 'g2_03cd', 'g2_03cm', 'g2_03cy', 'g2_03dd', 'g2_03dm', 'g2_03dy', 'g2_03ed', 'g2_03em', 'g2_03ey', 'g2_03fd', 'g2_03fm', 'g2_03fy', 'g3_01', 'g4_02', 'g4_03a', 'g4_03b', 'g4_04', 'g4_05', 'g4_06', 'g4_07', 'g4_08', 'g5_01d', 'g5_01m', 'g5_01y', 'g5_03d', 'g5_03m', 'g5_03y', 'g5_05', 'g5_06a', 'g5_06b', 'g5_07', 'g5_08']

neo_acceptible = {'c1_01' : [1, 2, 8, 9], 'c1_02' : [1, 2, 3, 8, 9], 'c1_03' : [0, 1, 8, 9], 'c1_04' : [1, 2, 8, 9],
'c1_06a' : [1, 2, 3, 4, 5, 8, 9], 'c1_07' : [1, 2, 3, 4, 8, 9], 'c1_09' : [1, 2, 8, 9], 'c1_11' : [1, 2, 8, 9], 'c1_12' : [0, 1, 8, 9],
'c1_13' : [0, 1, 8, 9], 'c1_14' : [0, 1, 8, 9], 'c1_15' : [0, 1, 8, 9], 'c1_16' : [0, 1, 8, 9], 'c1_17' : [0, 1, 8, 9], 'c1_18' : [0, 1, 8, 9], 'c1_19_1' : [0, 1, 8, 9],
'c1_19_2' : [0, 1, 8, 9], 'c1_19_3' : [0, 1, 8, 9], 'c1_19_4a' : [0, 1, 8, 9],
'c1_22a' : [1, 2, 3, 4, 5, 8, 9], 'c1_26' : [0, 1, 2], 'c2_01_1' : [0, 1, 8, 9], 'c2_01_2' : [0, 1, 8, 9], 'c2_01_3' : [0, 1, 8, 9],
 'c2_01_4' : [0, 1, 8, 9], 'c2_01_5' : [0, 1, 8, 9], 'c2_01_6' : [0, 1, 8, 9], 'c2_01_7' : [0, 1, 8, 9], 'c2_01_8' : [0, 1, 8, 9], 'c2_01_9' : [0, 1, 8, 9],
 'c2_01_10' : [0, 1, 8, 9], 'c2_01_12' : [0, 1, 8, 9], 'c2_03' : [1, 2, 3, 8, 9], 'c2_04' : [0, 1, 8, 9],
 'c2_06' : [1, 2, 8, 9], 'c2_07' : [1, 2, 8, 9], 'c2_08a' : [1, 2, 3, 8, 9], 'c2_09' : [0, 1, 8, 9],
 'c2_11' : [0, 1, 8, 9], 'c2_12' : [1, 2, 3, 4, 5, 8, 9], 'c2_13a' : [1, 2, 3, 4, 5, 8, 9], 'c2_15a' : [1, 2, 3, 4, 5, 6, 8, 9], 'c2_17' : [1, 2, 3, 4, 8, 9],
 'c2_18' : [0, 1, 8, 9], 'c3_01' : [0, 1, 8, 9], 'c3_02' : [0, 1, 8, 9], 'c3_03_1' : [0, 1, 8, 9], 'c3_03_2' : [0, 1, 8, 9], 'c3_03_3' : [0, 1, 8, 9],
 'c3_04' : [0, 1, 8, 9], 'c3_05' : [0, 1, 8, 9], 'c3_06' : [0, 1, 8, 9], 'c3_07' : [0, 1, 8, 9], 'c3_08' : [1, 2, 3, 4, 8, 9], 'c3_09' : [0, 1, 8, 9],
 'c3_10' : [1, 2, 8, 9], 'c3_11' : [0, 1, 8, 9], 'c3_12' : [0, 1, 8, 9], 'c3_13' : [0, 1, 8, 9], 'c3_15' : [1, 2, 8, 9],
 'c3_16' : [0, 1, 8, 9], 'c3_17' : [0, 1, 8, 9], 'c3_20' : [0, 1, 8, 9],
 'c3_23' : [0, 1, 8, 9], 'c3_24' : [0, 1, 8, 9], 'c3_25' : [0, 1, 8, 9],
 'c3_26' : [0, 1, 8, 9], 'c3_29' : [0, 1, 8, 9], 'c3_32' : [0, 1, 8, 9], 'c3_33' : [0, 1, 8, 9], 'c3_34' : [0, 1, 8, 9], 'c3_35' : [0, 1, 8, 9], 'c3_36' : [0, 1, 8, 9],
 'c3_37' : [0, 1, 8, 9], 'c3_38' : [0, 1, 8, 9], 'c3_39' : [0, 1, 8, 9], 'c3_40' : [0, 1, 8, 9], 'c3_41' : [0, 1, 8, 9], 'c3_42' : [0, 1, 8, 9], 'c3_44' : [0, 1, 8, 9],
 'c3_46' : [0, 1, 8, 9], 'c3_47' : [0, 1, 8, 9], 'c3_48' : [0, 1, 8, 9], 'c3_49' : [0, 1, 8, 9], 'c5_17' : [0, 1, 8, 9], 'c5_18' : [0, 1, 8, 9],
 'c5_19' : [0, 1, 8, 9], 'g5_02' : [1, 2, 8, 9]}

neo_variables = ['c1_01', 'c1_02', 'c1_03', 'c1_04', 'c1_04', 'c1_05a', 'c1_06a', 'c1_07', 'c1_08b', 'c1_09', 'c1_11', 'c1_12', 'c1_13', 'c1_14', 'c1_15', 'c1_16', 'c1_17', 'c1_18', 'c1_19_1', 'c1_19_2', 'c1_19_3', 'c1_19_4a', 'c1_20a', 'c1_21a', 'c1_22a', 'c1_25a', 'c1_26', 'c2_01_1', 'c2_01_2', 'c2_01_3', 'c2_01_4', 'c2_01_5', 'c2_01_6', 'c2_01_7', 'c2_01_8', 'c2_01_9', 'c2_01_10', 'c2_01_12', 'c2_02a', 'c2_03', 'c2_03', 'c2_04', 'c2_05a', 'c2_06', 'c2_07', 'c2_08a', 'c2_09', 'c2_10a', 'c2_11', 'c2_12', 'c2_13a', 'c2_15a', 'c2_17', 'c2_17', 'c2_17', 'c2_17', 'c2_18', 'c3_01', 'c3_02', 'c3_03_1', 'c3_03_2', 'c3_03_3', 'c3_04', 'c3_05', 'c3_06', 'c3_07', 'c3_08', 'c3_09', 'c3_10', 'c3_11', 'c3_12', 'c3_13', 'c3_14a', 'c3_15', 'c3_16', 'c3_17', 'c3_18a', 'c3_19a', 'c3_20', 'c3_21a', 'c3_22a', 'c3_23', 'c3_24', 'c3_25', 'c3_26', 'c3_27a', 'c3_28a', 'c3_29', 'c3_30a', 'c3_31a', 'c3_32', 'c3_33', 'c3_34', 'c3_35', 'c3_36', 'c3_37', 'c3_38', 'c3_39', 'c3_40', 'c3_41', 'c3_42', 'c3_44', 'c3_45a', 'c3_46', 'c3_47', 'c3_48', 'c3_49', 'c5_07', 'c5_07', 'c5_17', 'c5_18', 'c5_19', 'c3_43', ' c5_09', ' c5_12', 'c5_13', 'c5_14', 'c5_15', 'c5_16', 'c6_01', 'c6_02', 'c6_03', 'c6_04', 'c6_05', 'c6_06', 'c6_07', 'c6_08', 'c6_09', 'c6_10', 'g5_02', 'g5_04']

svars = ['sid', 'sex', 'age', 's5', 's6', 's7', 's8991', 's8992', 's9', 's11991', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21', 's22', 's23', 's24', 's25', 's26', 's27', 's28', 's29', 's30991', 's31', 's32', 's33', 's34', 's35', 's36', 's37', 's38', 's39', 's40', 's41', 's42', 's43', 's45', 's46991', 's46992', 's47', 's48', 's49991', 's50991', 's51991', 's52', 's53', 's54', 's55991', 's56991', 's57991', 's58991', 's58992', 's58993', 's58994', 's59', 's60', 's61', 's62', 's63', 's64', 's65', 's66', 's67', 's68', 's69991', 's70', 's71991', 's72', 's73', 's74', 's75', 's76991', 's77', 's78', 's79', 's80', 's81', 's82', 's83', 's84', 's85', 's86', 's87', 's88', 's89', 's90', 's91', 's92', 's93', 's94', 's95', 's96', 's97', 's98', 's99', 's100', 's101', 's102', 's103', 's104', 's105', 's106', 's107', 's108', 's109', 's180', 's181', 's188', 's189', 's190', 's99991', 's999910', 's999911', 's999912', 's999913', 's999914', 's999915', 's999916', 's999917', 's999918', 's999919', 's99992', 's999920', 's999921', 's999922', 's999923', 's999924', 's999925', 's999926', 's999927', 's999928', 's999929', 's99993', 's999930', 's999931', 's999932', 's999933', 's999934', 's999935', 's999936', 's999937', 's999938', 's999939', 's99994', 's99995', 's99996', 's99997', 's99998', 's99999', 's999940', 's999950', 's999941', 's999951', 's999942', 's999952', 's999943', 's999953', 's999944', 's999954', 's999945', 's999946', 's999947', 's999948', 's999949']

text_columns = ['c3_43', 'c5_09', 'c5_12', 'c5_13', 'c5_14', 'c5_15', 'c5_16', 'c6_01', 'c6_02', 'c6_03', 'c6_04', 'c6_05', 'c6_06', 'c6_07', 'c6_08', 'c6_09', 'c6_10']

duration_vars = ['c1_05a', 'c1_08b', 'c1_20a', 'c1_21a', 'c1_25a', 'c2_02a', 'c2_05a', 'c2_10a', 'c3_14a', 'c3_18a', 'c3_19a', 'c3_21a', 'c3_22a', 'c3_27a', 'c3_28a', 'c3_30a', 'c3_31a']

def zero(arrayVar):
    tempDict = {}
    for val in arrayVar:
        tempDict[val] = 0
    return tempDict

age = 0
# algorithm for finding bad inputs
def a():
    inputfile = "/Users/carlhartung/Desktop/testing.csv"
    spamReader = csv.reader(open(inputfile, 'rbU'))
    spamWriter = csv.writer(open('intermediate.csv', 'wb'))
    
    spamWriter.writerow(svars)
    
    column_headers = {}
    skip = []
    header_row = []
    for (index, row) in enumerate(spamReader):
        if (index == 0):
            # first row is headers
            for (col_i, column) in enumerate(row):
                if not(column in neo_variables or column in neonate_skip):
                    #print column in neonate_map
                    #print column in neonate_skip
                    print 'warning: ' + column + " unknown. Proceeding without using this column"
                    # for now just skip unknown column headers.. later this should be an error
                    skip.append(col_i)
                else:
                    # print 'replacing with ' + neonate_map[column]
                    
                    # build a map of {index, header}
                    #print 'putting ' + column + ' in ' + str(col_i)
                    column_headers.update({col_i : column})
            
            # for i in column_headers:
            #     print str(i)
            #     header_row.append(column_headers[i])
            # spamWriter.writerow(header_row)
        else:
            soutput = zero(svars)
            for (col_i, column) in enumerate(row):
                # skip over the irrelevant columns
                if col_i in skip:
                    continue
                    
                # no need to verify inputs for text and number fields
                if (column_headers[col_i] in text_columns or column_headers[col_i] in duration_vars):
                    continue
                    
                # skip over blank answers
                if column is None or column is '':
                    continue
                
                # check the rest to make sure they're acceptible answers
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
            outputrow = []
            for s in svars:
                outputrow.append(soutput[s])
            spamWriter.writerow(outputrow)
            print soutput
            print outputrow

#algorithm for converting inputs
def b():
    print 'woot'
                
    
    # once we've verified everything, go ahead and write the new s column headers to a file, along with all the data


algorithm(inputfile = "/Users/carlhartung/Desktop/SmartVA/Examples/NeonateuniformTrain-new.csv")



# The following methods convert the "c" variables into "s" variables with their appropriate values.
# The "s" values already start at zero, so these only need to change them to 1 if appropriate

def sid(value):
    return {'sid' : value}

def c1_01(value):
    print "found value " + str(value)
    if int(value) == 2:
        return {'s5' : 1}

def c1_02(value):
    if int(value) == 2 or int(value) == 3:
        return {'s6': 1}

def c1_03(value):
    if int(value) == 1:
        return {'s7', 1}

def c1_04(value):
    returndict = {}
    if int(value) == 1:
        returndict['s8991'] = 1
    elif int(value) == 2:
        returndict['s8992'] = 1
    return returndict

def c1_06a(value):
    if int(value) == 4 or int(value) == 5:
        return {'s11991': 1}

def c1_07(value):
    if int(value) == 1 or int(value) == 2:
        return {'s13': 1}

def c1_09(value):
    if int(value) == 1:
        return {'s15': 0}
    elif int(value) == 2:
        return {'s15' : 1}
    else:
        return {'s15' : 9999}

def c1_11(value):
    if int(value) == 2:
        return {'s16': 1}

def c1_12(value):
    if int(value) == 1:
        return {'s17': 1}

def c1_13(value):
    if int(value) == 1:
        return {'s18': 1}

def c1_14(value):
    if int(value) == 1:
        return {'s19': 1}

def c1_15(value):
    if int(value) == 1:
        return {'s20': 1}

def c1_16(value):
    if int(value) == 1:
        return {'s21': 1}

def c1_17(value):
    if int(value) == 1:
        return {'s22': 1}

def c1_18(value):
    if int(value) == 1:
        return {'s23': 1}

def c1_19_1(value):
    if int(value) == 1:
        return {'s24': 1}

def c1_19_2(value):
    if int(value) == 1:
        return {'s25': 1}

def c1_19_3(value):
    if int(value) == 1:
        return {'s26': 1}

def c1_19_4a(value):
    if int(value) == 1:
        return {'s27': 1}

def c1_22a(value):
    if int(value) == 3 or int(value) == 4:
           return {'s30991': 1}

def c1_26(value):
    if int(value) == 1:
        return {'s32': 1}

def c2_01_1(value):
    if int(value) == 2:
        return {'s33': 1}

def c2_01_2(value):
    if int(value) == 1:
        return {'s34': 1}

def c2_01_3(value):
    if int(value) == 1:
        return {'s35': 1}

def c2_01_4(value):
    if int(value) == 1:
        return {'s36': 1}

def c2_01_5(value):
    if int(value) == 1:
        return {'s37': 1}

def c2_01_6(value):
    if int(value) == 1:
        return {'s38': 1}

def c2_01_7(value):
    if int(value) == 1:
        return {'s39': 1}

def c2_01_8(value):
    if int(value) == 1:
        return {'s40': 1}

def c2_01_9(value):
    if int(value) == 1:
        return {'s41': 1}

def c2_01_10(value):
    if int(value) == 1:
        return {'s42': 1}

def c2_01_12(value):
    if int(value) == 1:
        return {'s43': 1}
 

def c2_03(value):
    returndict = {}
    if int(value) == 1:
        returndict['s46991'] = 1
    elif int(value) == 3:
        returndict['s36992'] = 1
    return returndict

def c2_04(value):
    if int(value) == 1:
      return {'s47': 1}

def c2_06(value):
    if int(value) == 2:
      return {'s4999a': 1}

def c2_06(value):
    if int(value) == 2:
        return {'s4999a': 1}

def c2_07(value):
    if int(value) == 2:
        return {'s50991': 1}

def c2_08a(value):
    if int(value) == 1 or int(value) == 3:
        return {'s51991': 1}

def c2_09(value):
    if int(value) == 1:
        return {'s52': 1}

def c2_11(value):
    if int(value) == 1:
        return {'s54': 1}
 

def c2_12(value):
    if int(value) == 1 or int(value) == 2:
        return {'s55991': 1}

def c2_13a(value):
    if int(value) == 4 or int(value) == 5:
        return {'s56991': 1}

def c2_15a(value):
    if not (int(value) == 1 or int(value) == 2):
        return {'s57991': 1}

def c2_17(value):
    returndict = {}
    if int(value) == 1:
        returndict['s58991'] = 1
    elif int(value) == 2:
        returndict['s58992'] = 1
    elif int(value) == 3:
        returndict['s58993'] = 1
    elif int(value) == 4:
        returndict['s58994'] = 1
    return returndict

def c2_18(value):
    if int(value) == 1:
        return {'s59': 1}

def c3_01(value):
    if int(value) == 1:
        return {'s60': 1}

def c3_02(value):
    if int(value) == 1:
        return {'s61': 1}

def c3_03_1(value):
    if int(value) == 1:
        return {'s62': 1}

def c3_03_2(value):
    if int(value) == 1:
        return {'s63': 1}

def c3_03_3(value):
    if int(value) == 1:
        return {'s64': 1}

def c3_04(value):
    if int(value) == 1:
        return {'s65': 1}

def c3_05(value):
    if int(value) == 1:
        return {'s66': 1}

def c3_06(value):
    if int(value) == 1:
        return {'s67': 1}

def c3_07(value):
    if int(value) == 1:
        return {'s68': 1}

def c3_08(value):
    if int(value) == 3 or int(value) == 4:
        return {'s69991': 1}

def c3_09(value):
    if int(value) == 1:
        return {'s70': 1}

def c3_10(value):
    if int(value) == 2:
        return {'s71991': 1}

def c3_11(value):
    if int(value) == 1:
        return {'s72': 1}

def c3_12(value):
    if int(value) == 1:
        return {'s73': 1}

def c3_13(value):
    if int(value) == 1:
        return {'s74': 1}

def c3_15(value):
    if int(value) == 2:
        return {'s76991': 1}

def c3_16(value):
    if int(value) == 1:
        return {'s77': 1}

def c3_17(value):
    if int(value) == 1:
        return {'s78': 1}

def c3_20(value):
    if int(value) == 1:
        return {'s81': 1}

def c3_23(value):
    if int(value) == 1:
        return {'s84': 1}

def c3_24(value):
    if int(value) == 1:
        return {'s85': 1}

def c3_25(value):
    if int(value) == 1:
        return {'s86': 1}

def c3_26(value):
    if int(value) == 1:
        return {'s87': 1}

def c3_29(value):
    if int(value) == 1:
        return {'s90': 1}

def c3_32(value):
    if int(value) == 1:
        return {'s93': 1}

def c3_33(value):
    if int(value) == 1:
        return {'s94': 1}

def c3_34(value):
    if int(value) == 1:
        return {'s95': 1}

def c3_35(value):
    if int(value) == 1:
        return {'s96': 1}

def c3_36(value):
    if int(value) == 1:
        return {'s97': 1}

def c3_37(value):
    if int(value) == 1:
        return {'s98': 1}

def c3_38(value):
    if int(value) == 1:
        return {'s99': 1}

def c3_39(value):
    if int(value) == 1:
        return {'s100': 1}

def c3_40(value):
    if int(value) == 1:
        return {'s101': 1}

def c3_41(value):
    if int(value) == 1:
        return {'s102': 1}

def c3_42(value):
    if int(value) == 1:
        return {'s103': 1}

def c3_44(value):
    if int(value) == 1:
        return {'s104': 1}

def c3_45a(value):
    if int(value) > 1:
        return {'s105': 1}

def c3_46(value):
    if int(value) == 1:
        return {'s106': 1}

def c3_47(value):
    if int(value) == 1:
        return {'s107': 1}

def c3_48(value):
    if int(value) == 1:
        return {'s108': 1}

def c3_49(value):
    if int(value) == 1:
        return {'s109': 1}

def c5_07(value):
    returndict = {}
    if int(value) == 9999:
        returndict['s180'] = 9999
        returndict['s181'] = 9999
    return returndict

def c5_17(value):
    if int(value) == 1:
        return {'s188': 1}

def c5_18(value):
    if int(value) == 1:
        return {'s189': 1}

def c5_19(value):
    if int(value) == 1:
        return {'s190': 1}
        
def g5_02(value):
    if int(value) == 1:
        return {'sex': 0}
    elif int(value) == 2:
        return {'sex' : 1}
    else:
        return {'sex' : 9999}

def g5_04a(value):
    age += value * 365
    return cal_age()

def g5_04b(value):
    age += value * 30
    return cal_age()

def g5_04c(value):
    age += value
    return cal_age()
    
def cal_age():
    returndict = {}
    if age == 0:
        returndict['s4991'] = 1
        returndict['s4992'] = 0
        returndict['s4993'] = 0
    elif age == 1 or age == 2:
        returndict['s4991'] = 0
        returndict['s4992'] = 1
        returndict['s4993'] = 0
    else:
        returndict['s4991'] = 0
        returndict['s4992'] = 0
        returndict['s4993'] = 1
    return returndict
    
    
    1 if g4_04a * 365 + g5_04b*30 + g5_04a == 0	s4991
1 if g4_04a * 365 + g5_04b*30 + g5_04a == 1 or 2	s4993
1 if g4_04a * 365 + g5_04b*30 + g5_04a >= 3	s4994

# these are all the text variables

def wordsearch(value):
    returndict = {}
    if value is None:
        return {}
    if 'abdomen' in value:
        returndict['s99991'] = 1
    if 'cesarean' in value:
        returndict['s999910'] = 1
    if 'child' in value:
        returndict['s999911'] = 1
    if 'color' in value:
        returndict['s999912'] = 1
    if 'cord' in value:
        returndict['s999913'] = 1
    if 'cri' in value:
        returndict['s999914'] = 1
    if 'dead' in value:
        returndict['s999915'] = 1
    if 'difficult' in value:
        returndict['s999916'] = 1
    if 'distress' in value:
        returndict['s999917'] = 1
    if 'fetal' in value:
        returndict['s999918'] = 1
    if 'fever' in value:
        returndict['s999919'] = 1
    if 'aliv' in value:
        returndict['s99992'] = 1
    if 'glucos' in value:
        returndict['s999920'] = 1
    if 'head' in value:
        returndict['s999921'] = 1
    if 'heart' in value:
        returndict['s999922'] = 1
    if 'heartbeat' in value:
        returndict['s999923'] = 1
    if 'bemorrhag' in value:
        returndict['s999924'] = 1
    if 'hiv' in value:
        returndict['s999925'] = 1
    if 'hypertens' in value:
        returndict['s999926'] = 1
    if 'incub' in value:
        returndict['s999927'] = 1
    if 'induc' in value:
        returndict['s999928'] = 1
    if 'infect' in value:
        returndict['s999929'] = 1
    if 'anemia' in value:
        returndict['s99993'] = 1
    if 'injuri' in value:
        returndict['s999930'] = 1
    if 'labor' in value:
        returndict['s999931'] = 1
    if 'live' in value:
        returndict['s999932'] = 1
    if 'lung' in value:
        returndict['s999933'] = 1
    if 'movement' in value:
        returndict['s999934'] = 1
    if 'oxygen' in value:
        returndict['s999935'] = 1
    if 'pain' in value:
        returndict['s999936'] = 1
    if 'pneumonia' in value:
        returndict['s999937'] = 1
    if 'pregnanc' in value:
        returndict['s999938'] = 1
    if 'prenat' in value:
        returndict['s999939'] = 1
    if 'ashpyxia' in value:
        returndict['s99994'] = 1
    if 'babi' in value:
        returndict['s99995'] = 1
    if 'blood' in value:
        returndict['s99996'] = 1
    if 'born' in value:
        returndict['s99997'] = 1
    if 'breech' in value:
        returndict['s99998'] = 1
    if 'bwt' in value:
        returndict['s99999'] = 1
    if 'preterm' in value:
        returndict['s999940'] = 1
    if 'twin' in value:
        returndict['s999950'] = 1
    if 'renal' in value:
        returndict['s999941'] = 1
    if 'urin' in value:
        returndict['s999951'] = 1
    if 'respiratori' in value:
        returndict['s999942'] = 1
    if 'ventil' in value:
        returndict['s999952'] = 1
    if 'section' in value:
        returndict['s999943'] = 1
    if 'vomit' in value:
        returndict['s999953'] = 1
    if 'sepsi' in value:
        returndict['s999944'] = 1
    if 'weight' in value:
        returndict['s999954'] = 1
    if 'sever' in value:
        returndict['s999945'] = 1
    if 'skin' in value:
        returndict['s999946'] = 1
    if 'stillbirth' in value:
        returndict['s999947'] = 1
    if 'stomach' in value:
        returndict['s999948'] = 1
    if 'swell' in value:
        returndict['s999949'] = 1


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

#duration variables
def c1_05a(value):
    if int(value) >= 5:
        return {'s9': 1}

def c1_08b (value):
    if int(value) >= 2500:
        return {'s14': 1}

def c1_20a (value):
    if int(value) >= 2:
        return {'s28': 1}

def c1_21a (value):
    if int(value) >= 3:
        return {'s29': 1}

def c1_25a (value):
    if int(value) >= 3:
        return {'s31': 1}
        
def c2_02a (value):
    if int(value) >= 270:
        return {'s45': 1}

def c2_05a (value):
    if int(value) >= .2916667:
        return {'s48': 1}

def c2_10a (value):
    if int(value) >= .3333333:
        return {'s53': 1}

def c3_14a (value):
    if int(value) >= 2:
        return {'s74': 1}

def c3_18a (value):
    if int(value) >= 2:
        return {'s79': 1}

def c3_19a (value):
    if int(value) >= 2:
        return {'s80': 1}

def c3_21a (value):
    if int(value) >= 2:
        return {'s82': 1}

def c3_22a (value):
    if int(value) >= 2:
        return {'s83': 1}

def c3_27a (value):
    if int(value) >= 3:
        return {'s88': 1}

def c3_28a (value):
    if int(value) >= 2:
        return {'s89': 1}

def c3_30a (value):
    if int(value) >= 3:
        return {'s91': 1}

def c3_31a (value):
    if int(value) >= 2:
        return {'s92': 1}



# maps strings to functions.  i.e. 'c1_01' to c1_01()
fmap = dict(sid=sid, c1_01=c1_01, c1_02=c1_02, c1_03=c1_03, c1_04=c1_04, c1_05a=c1_05a, c1_06a=c1_06a, c1_07=c1_07, c1_08b=c1_08b, c1_09=c1_09, c1_11=c1_11, c1_12=c1_12, c1_13=c1_13,
c1_14=c1_14, c1_15=c1_15, c1_16=c1_16, c1_17=c1_17, c1_18=c1_18, c1_19_1=c1_19_1, c1_19_2=c1_19_2, c1_19_3=c1_19_3, c1_19_4a=c1_19_4a, c1_20a=c1_20a, c1_21a=c1_21a,
c1_22a=c1_22a, c1_25a=c1_25a, c1_26=c1_26, c2_01_1=c2_01_1, c2_01_2=c2_01_2, c2_01_3=c2_01_3, c2_01_4=c2_01_4, c2_01_5=c2_01_5, c2_01_6=c2_01_6, c2_01_7=c2_01_7,
c2_01_8=c2_01_8, c2_01_9=c2_01_9, c2_01_10=c2_01_10, c2_01_12=c2_01_12, c2_02a=c2_02a, c2_03=c2_03, c2_04=c2_04, c2_05a=c2_05a, c2_06=c2_06, c2_07=c2_07, c2_08a=c2_08a,
c2_09=c2_09, c2_10a=c2_10a, c2_11=c2_11, c2_12=c2_12, c2_13a=c2_13a, c2_15a=c2_15a, c2_17=c2_17, c2_18=c2_18, c3_01=c3_01, c3_02=c3_02, c3_03_1=c3_03_1, c3_03_2=c3_03_2,
c3_03_3=c3_03_3, c3_04=c3_04, c3_05=c3_05, c3_06=c3_06, c3_07=c3_07, c3_08=c3_08, c3_09=c3_09, c3_10=c3_10, c3_11=c3_11, c3_12=c3_12, c3_13=c3_13, c3_14a=c3_14a,
c3_15=c3_15, c3_16=c3_16, c3_17=c3_17, c3_18a=c3_18a, c3_19a=c3_19a, c3_20=c3_20, c3_21a=c3_21a, c3_22a=c3_22a, c3_23=c3_23, c3_24=c3_24, c3_25=c3_25, c3_26=c3_26,
 c3_27a=c3_27a, c3_28a=c3_28a, c3_29=c3_29, c3_30a=c3_30a, c3_31a=c3_31a, c3_32=c3_32, c3_33=c3_33, c3_34=c3_34, c3_35=c3_35, c3_36=c3_36, c3_37=c3_37, c3_38=c3_38,
  c3_39=c3_39, c3_40=c3_40, c3_41=c3_41, c3_42=c3_42, c3_44=c3_44, c3_45a=c3_45a, c3_46=c3_46, c3_47=c3_47, c3_48=c3_48, c3_49=c3_49, c5_07=c5_07, c5_17=c5_17,
  c5_18=c5_18, c5_19=c5_19, c3_43=c3_43, c5_09=c5_09, c5_12=c5_12, c5_13=c5_13, c5_14=c5_14, c5_15=c5_15, c5_16=c5_16, c6_01=c6_01, c6_02=c6_02, c6_03=c6_03,
  c6_04=c6_04, c6_05=c6_05, c6_06=c6_06, c6_07=c6_07, c6_08=c6_08, c6_09=c6_09, c6_10=c6_10, g5_02=g5_02, g5_04=g5_04)


# def myfun(column, value):
#     if column is 'c1_01':
#         if value == 2:
#             return ['s5', 1]
#         else:
#             return ['s5', 2]




