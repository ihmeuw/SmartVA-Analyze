from __future__ import print_function
import csv
from datetime import date
import os

from dateutil.relativedelta import relativedelta

from smartva.default_fill_data import CHILD_DEFAULT_FILL, CHILD_DEFAULT_FILL_SHORT
from smartva.answer_ranges import CHILD_RANGE_LIST
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.utils.conversion_utils import additional_headers_and_values, check_skip_patterns, int_value_or_0
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier, get_item_count
from smartva.child_pre_symptom_data import (
    DURATION_VARS,
    GENERATED_VARS_DATA,
    VAR_CONVERSION_MAP,
    RECODE_MAP,
    FREE_TEXT_VARS,
    SHORT_FORM_FREE_TEXT_CONVERSION,
    BINARY_CONVERSION_MAP,
    SKIP_PATTERN_DATA,
    DURATION_VARS_SPECIAL_CASE,
    DURATION_VARS_SHORT_FORM_DROP_LIST,
    WEIGHT_VARS,
    DATE_VARS,
    EXAM_DATE_VARS,
    DOB_VAR, SEX_VAR,
    MALE_SD3, FEMALE_SD3,
    MALE_SD2, FEMALE_SD2
)
from smartva.word_conversions import CHILD_WORDS_TO_VARS

DROP_PATTERN = '[a]([_\d]|dult)'


# NOTES:
# these variables don't exist in the electronic version of the form:
# c1_09, c1_10, c1_10d, c1_10m, c1_10y, c1_19_6, c1_24, c1_24d, c1_24m, c1_24y, c1_26, c4_31_2, c5_02_11b


class ChildPreSymptomPrep(PreSymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        PreSymptomPrep.__init__(self, input_file, output_dir, short_form)
        self.AGE_GROUP = 'child'

    def run(self):
        super(ChildPreSymptomPrep, self).run()

        status_logger.info('{} :: Processing pre-symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        if self.short_form:
            default_fill = CHILD_DEFAULT_FILL_SHORT
        else:
            default_fill = CHILD_DEFAULT_FILL

        duration_vars = DURATION_VARS[:]

        if self.short_form:
            for var in DURATION_VARS_SHORT_FORM_DROP_LIST:
                duration_vars.remove(var)

        with open(os.path.join(self.output_dir, self.FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.writer(fo)

            with open(self.input_file_path, 'rb') as fi:
                reader = csv.reader(fi)
                records = get_item_count(reader, fi) - 1
                status_notifier.update({'sub_progress': (0, records)})

                headers = next(reader)

                additional_headers_data = GENERATED_VARS_DATA + [(k, '') for k in DURATION_VARS]
                additional_headers, additional_values = additional_headers_and_values(headers, additional_headers_data)

                headers.extend(additional_headers)

                self.rename_headers(headers, VAR_CONVERSION_MAP)

                drop_index_list = self.get_drop_index_list(headers, DROP_PATTERN)
                drop_index_list += self.get_drop_index_list(headers, 'child')
                drop_index_list += [headers.index('{}a'.format(header)) for header in DURATION_VARS]
                drop_index_list += [headers.index('{}b'.format(header)) for header in DURATION_VARS]

                writer.writerow(self.drop_from_list(headers, drop_index_list))

                for index, row in enumerate(reader):
                    if self.want_abort:
                        return False

                    status_notifier.update({'sub_progress': 1})

                    new_row = row + additional_values

                    self.verify_answers_for_row(headers, new_row, CHILD_RANGE_LIST)

                    self.convert_free_text_headers(headers, new_row, FREE_TEXT_VARS, CHILD_WORDS_TO_VARS)

                    if self.short_form:
                        word_list = [v for k, v in SHORT_FORM_FREE_TEXT_CONVERSION.items() if
                                     new_row[headers.index(k)] in [1, '1']]
                        if word_list:
                            self.convert_free_text_words(headers, new_row, word_list, CHILD_WORDS_TO_VARS)

                    self.recode_answers(headers, new_row, RECODE_MAP)

                    self.convert_binary_variables(headers, new_row, BINARY_CONVERSION_MAP.items())

                    check_skip_patterns(headers, new_row, SKIP_PATTERN_DATA, default_fill)
                    # special case skip patterns

                    self.calculate_duration_variables(headers, new_row, duration_vars, DURATION_VARS_SPECIAL_CASE)

                    self.fill_missing_data(headers, new_row, default_fill)

                    for var in WEIGHT_VARS:
                        if int_value_or_0(new_row[headers.index(var)]) in [0, 9999]:
                            new_row[headers.index(var)] = ''

                    # Get an approximate date.
                    # Add 'd' (day) 'm' (month) 'y' (years) to each var and process.
                    vals = {
                        'd': (['', '99', 99], 1),
                        'm': (['', '99', 99], 1),
                        'y': (['', '999', 999, '9999', 9999], 0),
                    }
                    for var in DATE_VARS:
                        for val, val_data in vals.items():
                            var_name = var + val
                            invalid_data, default = val_data
                            if new_row[headers.index(var_name)] in invalid_data:
                                new_row[headers.index(var_name)] = default

                    # Get most recent weight from medical records
                    if int(row[headers.index('{:s}y'.format(DOB_VAR))]):
                        try:
                            dob = make_date(headers, new_row, DOB_VAR)
                        except ValueError:
                            pass
                        else:

                            for var, weight in EXAM_DATE_VARS.items():
                                exam_data = []
                                for val in ['_1', '_2']:
                                    try:
                                        exam_date = make_date(headers, new_row, var + val)
                                    except ValueError:
                                        continue
                                    exam_weight = int(row[headers.index('{:s}{:s}b'.format(weight, val))])
                                    exam_data.append((exam_date, exam_weight))

                                if exam_data:
                                    latest_exam, latest_weight = sorted(exam_data, reverse=True)[0]

                                    if latest_exam > dob:
                                        age_at_exam = relativedelta(latest_exam, dob)
                                        age_at_exam_months = age_at_exam.years * 12 + age_at_exam.months

                                        if age_at_exam_months <= 60:
                                            sex = int(row[headers.index(SEX_VAR)])
                                            weight_kg = latest_weight / 1000

                                            sd3 = {(1, k): v for k, v in MALE_SD3.items()}
                                            sd3.update({(2, k): v for k, v in FEMALE_SD3.items()})

                                            sd2 = {(1, k): v for k, v in MALE_SD2.items()}
                                            sd2.update({(2, k): v for k, v in FEMALE_SD2.items()})

                                            if weight_kg < sd3.get((sex, age_at_exam_months)):
                                                row[headers.index('s180')] = 1
                                            if weight_kg < sd2.get((sex, age_at_exam_months)):
                                                row[headers.index('s181')] = 1

                    writer.writerow(self.drop_from_list(new_row, drop_index_list))


def make_date(headers, row, key):
    print(int(row[headers.index('{:s}y'.format(key))]),
                int(row[headers.index('{:s}m'.format(key))]),
                int(row[headers.index('{:s}d'.format(key))]))
    return date(int(row[headers.index('{:s}y'.format(key))]),
                int(row[headers.index('{:s}m'.format(key))]),
                int(row[headers.index('{:s}d'.format(key))]))


"""
# fix child agedays.  if it's blank give it a 0, if it's not, give it a 4
if row[headers.index('c1_25b')] == '' or row[headers.index('c1_25b')] is None:
    row[headers.index('c1_25a')] = '0'
else:
    row[headers.index('c1_25a')] = '4'

if (row[headers.index('c1_25b')] != '' and int(row[headers.index('c1_25b')]) >= 1 and int(
        row[headers.index('c1_25b')]) <= 28):
    row[headers.index('c1_26')] = '1'
"""

"""
# child rash, 4 = days
index = headers.index('c4_33b')
temp = row[headers.index('c4_33a')]
if temp != '4':
    # row[index] = row[headers_old.index('child_4_33a')]
    row[index] = '0'
"""
"""
# added for shortform
if self.short_form:

    # change stools answer from 2 to 1. why?
    index = headers.index('c4_08a')
    temp = row[headers_old.index('child_4_8')]
    if temp == '2':
        row[index] = '1'

    # convert to check skip pattern? {'(c4_07a=1)': ['c4_07b']}
    index = headers.index('c4_07b')
    testval = row[headers.index('c4_07a')]
    if testval != '1':
        row[index] = '0'  # just to make sure that c4_07b doesn't get child_4_7a like in the long form
"""

"""
# Test skip patterns
for i, row in enumerate(matrix):
    # i starts at 0, header row is 1 in excel, so do i+2 for the actual data row

    c3_11 = row[headers.index('c3_11')]
    # This is a unique case because c3_12 can have different 'default' values depending on other variables
    if c1_15 == '1':
        c3_12 = row[headers.index('c3_12')]
        if c3_12 != '0':
            updatestr = 'Child :: Value at row %s col %s for variable c3_12 should be 0, setting to 0 and continuing' % (i + 2, headers.index('c3_12'))
            warning_logger.warning(updatestr)
            row[headers.index('c3_12')] = '0'
    elif c1_26 == '2' or c3_11 == '1':
        c3_12 = row[headers.index('c3_12')]
        if c3_12 != '1':
            updatestr = 'Child :: Value at row %s col %s for variable c3_12 should be 1, setting to default and continuing' % (i + 2, headers.index('c3_12'))
            warning_logger.warning(updatestr)
            row[headers.index('c3_12')] = '1'
    c3_12 = row[headers.index('c3_12')]

"""

"""
# special case: 'child_4_50b' should be set to 1000 if it's missing
for row in matrix:
    if row[headers.index('child_4_50b')] == '' or row[headers.index('child_4_50b')] is None:
        row[headers.index('child_4_50b')] = 1000

"""
"""
# fix missingness coding for weight from medical record
for row_i, row in enumerate(matrix):

        knownAge = True
        if row[g5_01y] == 0:
            knownAge = False

        if knownAge:
            # generate how many months after Jan 1 1960 they were born - This is a specific stata function

            base_date = date(1960, 1, 1)
            delta = relativedelta(date(int(row[g5_01y]), int(row[g5_01m]), int(row[g5_01d])), base_date)
            mofd = delta.years * 12 + delta.months

            mofm1 = -1
            mofm2 = -1
            if row[c5_06_1y] != 0:
                exam1date = date(int(row[c5_06_1y]), int(row[c5_06_1m]), int(row[c5_06_1d]))
                exam1delta = relativedelta(exam1date, base_date)
                mofm1 = exam1delta.years * 12 + exam1delta.months

            if row[c5_06_2y] != 0:
                exam2date = date(int(row[c5_06_2y]), int(row[c5_06_2m]), int(row[c5_06_2d]))
                exam2delta = relativedelta(exam2date, base_date)
                mofm2 = exam2delta.years * 12 + exam2delta.months

            # if row[headers.index('sid')] == '627':
            #     print "mofm1 and mofm2 %s and %s" % (mofm1, mofm2)

            # identify most recent medical record
            # gen max_age = max(mofm1, mofm2)
            max_age = max(mofm1, mofm2)

            month = max_age - mofd

            p = 0

            # only keep going if they have a positive age in the right range
            if month >= 0 and month <= 60:
                # only child
                weight_kg = 0
                if max_age == mofm1 and row[headers.index('c5_07_1b')] != '':
                    weight_kg = float(row[headers.index('c5_07_1b')]) / 1000
                elif max_age == mofm2 and row[headers.index('c5_07_2b')] != '':
                    weight_kg = float(row[headers.index('c5_07_2b')]) / 1000

                if p == 1:
                    print "using weight %s" % weight_kg

                # input months, output 3rd standard deviation below
                male_sd3 = {0: 2.1, 1: 2.9, 2: 3.8, 3: 4.4, 4: 4.9, 5: 5.3, 6: 5.7, 7: 5.9, 8: 6.2, 9: 6.4,
                            10: 6.6, 11: 6.8, 12: 6.9, 13: 7.1, 14: 7.2, 15: 7.4, 16: 7.5, 17: 7.7, 18: 7.8,
                            19: 8, 20: 8.1, 21: 8.2, 22: 8.4, 23: 8.5, 24: 8.6, 25: 8.8, 26: 8.9, 27: 9,
                            28: 9.1, 29: 9.2, 30: 9.4, 31: 9.5, 32: 9.6, 33: 9.7, 34: 9.8, 35: 9.9, 36: 10,
                            37: 10.1, 38: 10.2, 39: 10.3, 40: 10.4, 41: 10.5, 42: 10.6, 43: 10.7, 44: 10.8,
                            45: 10.9, 46: 11, 47: 11.1, 48: 11.2, 49: 11.3, 50: 11.4, 51: 11.5, 52: 11.6,
                            53: 11.7, 54: 11.8, 55: 11.9, 56: 12, 57: 12.1, 58: 12.2, 59: 12.3, 60: 12.4}

                female_sd3 = {0: 2, 1: 2.7, 2: 3.4, 3: 4, 4: 4.4, 5: 4.8, 6: 5.1, 7: 5.3, 8: 5.6, 9: 5.8,
                              10: 5.9, 11: 6.1, 12: 6.3, 13: 6.4, 14: 6.6, 15: 6.7, 16: 6.9, 17: 7, 18: 7.2,
                              19: 7.3, 20: 7.5, 21: 7.6, 22: 7.8, 23: 7.9, 24: 8.1, 25: 8.2, 26: 8.4, 27: 8.5,
                              28: 8.6, 29: 8.8, 30: 8.9, 31: 9, 32: 9.1, 33: 9.3, 34: 9.4, 35: 9.5, 36: 9.6,
                              37: 9.7, 38: 9.8, 39: 9.9, 40: 10.1, 41: 10.2, 42: 10.3, 43: 10.4, 44: 10.5,
                              45: 10.6, 46: 10.7, 47: 10.8, 48: 10.9, 49: 11, 50: 11.1, 51: 11.2, 52: 11.3,
                              53: 11.4, 54: 11.5, 55: 11.6, 56: 11.7, 57: 11.8, 58: 11.9, 59: 12, 60: 12.1}

                male_sd2 = {0: 2.5, 1: 3.4, 2: 4.3, 3: 5, 4: 5.6, 5: 6, 6: 6.4, 7: 6.7, 8: 6.9, 9: 7.1, 10: 7.4,
                            11: 7.6, 12: 7.7, 13: 7.9, 14: 8.1, 15: 8.3, 16: 8.4, 17: 8.6, 18: 8.8, 19: 8.9,
                            20: 9.1, 21: 9.2, 22: 9.4, 23: 9.5, 24: 9.7, 25: 9.8, 26: 10, 27: 10.1, 28: 10.2,
                            29: 10.4, 30: 10.5, 31: 10.7, 32: 10.8, 33: 10.9, 34: 11, 35: 11.2, 36: 11.3,
                            37: 11.4, 38: 11.5, 39: 11.6, 40: 11.8, 41: 11.9, 42: 12, 43: 12.1, 44: 12.2,
                            45: 12.4, 46: 12.5, 47: 12.6, 48: 12.7, 49: 12.8, 50: 12.9, 51: 13.1, 52: 13.2,
                            53: 13.3, 54: 13.4, 55: 13.5, 56: 13.6, 57: 13.7, 58: 13.8, 59: 14, 60: 14.1}

                female_sd2 = {0: 2.4, 1: 3.2, 2: 3.9, 3: 4.5, 4: 5, 5: 5.4, 6: 5.7, 7: 6, 8: 6.3, 9: 6.5,
                              10: 6.7, 11: 6.9, 12: 7, 13: 7.2, 14: 7.4, 15: 7.6, 16: 7.7, 17: 7.9, 18: 8.1,
                              19: 8.2, 20: 8.4, 21: 8.6, 22: 8.7, 23: 8.9, 24: 9, 25: 9.2, 26: 9.4, 27: 9.5,
                              28: 9.7, 29: 9.8, 30: 10, 31: 10.1, 32: 10.3, 33: 10.4, 34: 10.5, 35: 10.7,
                              36: 10.8, 37: 10.9, 38: 11.1, 39: 11.2, 40: 11.3, 41: 11.5, 42: 11.6, 43: 11.7,
                              44: 11.8, 45: 12, 46: 12.1, 47: 12.2, 48: 12.3, 49: 12.4, 50: 12.6, 51: 12.7,
                              52: 12.8, 53: 12.9, 54: 13, 55: 13.2, 56: 13.3, 57: 13.4, 58: 13.5, 59: 13.6,
                              60: 13.7}

                if weight_kg > 0:
                    sex = row[headers.index('g5_02')]
                    if p == 1:
                        print "wtf %s %s %s %s " % (male_sd3[month], male_sd2[month], female_sd3[month], female_sd2[month])
                        print "testing %s" % (weight_kg < male_sd3[month])
                        print "sex ? %s" % sex

                    if sex == '1':
                        if weight_kg < male_sd3[month]:
                            row[headers.index('s180')] = 1
                        if weight_kg < male_sd2[month]:
                            row[headers.index('s181')] = 1
                    elif sex == '2':
                        if weight_kg < female_sd3[month]:
                            row[headers.index('s180')] = 1
                        if weight_kg < female_sd2[month]:
                            row[headers.index('s181')] = 1
"""
