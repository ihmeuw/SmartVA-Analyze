from __future__ import print_function
from smartva import child_pre_symptom_data
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.utils.conversion_utils import value_or_default


class ChildPreSymptomPrep(PreSymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        PreSymptomPrep.__init__(self, input_file, output_dir, short_form)
        self.AGE_GROUP = 'child'

        self.data_module = child_pre_symptom_data

        self._init_data_module()

    def run(self):
        super(ChildPreSymptomPrep, self).run()

    def pre_processing_step(self, row):
        self.fix_agedays(row)
        self.calculate_age_at_death_value(row)

    def fix_agedays(self, row):
        value = value_or_default(row['c1_25b'], int, default=None)
        if value is None:
            row['c1_25a'] = 0
        else:
            row['c1_25a'] = 4

    def calculate_age_at_death_value(self, row):
        row['c1_26'] = 2

    def post_processing_step(self, row):
        self.process_weight_sd_vars(row, self.data_module.EXAM_DATE_VARS, self.data_module.WEIGHT_SD_DATA)


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
child_1_8a = row[headers_old.index('child_1_8a')]
child_1_8b = row[headers_old.index('child_1_8b')]
if child_1_8a == '' or child_1_8a is None:
    child_1_8a = '0'
if child_1_8b == '' or child_1_8b is None:
    child_1_8b = '0'
if child_1_8b != 0:
    child_1_8b = int(child_1_8b) * 1000
row[headers.index('child_1_8num')] = float(child_1_8a) + float(child_1_8b)

child_1_8 = row[headers_old.index('child_1_8')]
if child_1_8 == '2':
    row[headers_old.index('child_1_8')] = '1'
"""

"""
#### Deviation from neonate!!!

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
##### Deviates from neonate
# special case: 'child_4_50b' should be set to 1000 if it's missing
for row in matrix:
    if row[headers.index('child_4_50b')] == '' or row[headers.index('child_4_50b')] is None:
        row[headers.index('child_4_50b')] = 1000

"""
