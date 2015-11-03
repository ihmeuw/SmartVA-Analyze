from __future__ import print_function
from smartva import adult_pre_symptom_data
from smartva.pre_symptom_prep import PreSymptomPrep


class AdultPreSymptomPrep(PreSymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        PreSymptomPrep.__init__(self, input_file, output_dir, short_form)
        self.AGE_GROUP = 'adult'

        self.data_module = adult_pre_symptom_data

        self._init_data_module()

    def run(self):
        super(AdultPreSymptomPrep, self).run()

    def post_processing_step(self, row):
        pass

    def pre_processing_step(self, row):
        pass
