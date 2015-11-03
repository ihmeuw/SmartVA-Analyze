from __future__ import print_function
from smartva import neonate_pre_symptom_data
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.utils.conversion_utils import value_or_default


class NeonatePreSymptomPrep(PreSymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        PreSymptomPrep.__init__(self, input_file, output_dir, short_form)
        self.AGE_GROUP = 'neonate'

        self.data_module = neonate_pre_symptom_data

        self._init_data_module()

    def run(self):
        super(NeonatePreSymptomPrep, self).run()

    def pre_processing_step(self, row):
        self.fix_agedays(row)
        self.calculate_age_at_death_value(row)

    def fix_agedays(self, row):
        # fix child agedays.  if it's blank give it a 0, if it's not, give it a 4
        value = value_or_default(row['c1_25b'], int, default=None)
        if value is None:
            row['c1_25a'] = 0
        else:
            row['c1_25a'] = 4

    def calculate_age_at_death_value(self, row):
        value = value_or_default(row['c1_25b'], int, default=None)
        if 1 <= value <= 28:
            row['c1_26'] = 1

    def post_processing_step(self, row):
        self.process_weight_sd_vars(row, self.data_module.EXAM_DATE_VARS, self.data_module.WEIGHT_SD_DATA)


"""
            index = headers.index('c4_33b')
            temp = row[headers.index('c4_33a')]
            if temp == '4':
                row[index] = row[headers_old.index('child_4_33a')]
"""
"""
                # index = headers.index('c4_08a')
                # temp = row[headers_old.index('child_4_8')]
                # if temp == '2':
                #     row[index] = '1'
"""
