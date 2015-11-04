from __future__ import print_function

from smartva import child_symptom_data
from smartva.symptom_prep import SymptomPrep


class ChildSymptomPrep(SymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        super(ChildSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = child_symptom_data

        self._init_data_module()

    def run(self):
        super(ChildSymptomPrep, self).run()


# TODO - child rash?
"""
# s139 can be multiple
index = headers.index('s139991')
val = row[headers.index('s139')]
if val == '':
    val = ['0']
else:
    val = val.split(' ')
if '1' in val:
    row[index] = '1'
"""

# TODO - child rash part 2?
"""
# s141 can me multiple, but we only care if 1 (and only 1) is selected
index = headers.index('s141991')
val = row[headers.index('s141')]
if val == '':
    val = ['0']
else:
    val = val.split(' ')
if '1' in val and len(val) == 1:
    row[index] = '1'
"""
