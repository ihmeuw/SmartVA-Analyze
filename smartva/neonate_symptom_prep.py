from __future__ import print_function

from smartva import neonate_symptom_data
from smartva.symptom_prep import SymptomPrep


class NeonateSymptomPrep(SymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        super(NeonateSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = neonate_symptom_data

        self._init_data_module()

    def run(self):
        super(NeonateSymptomPrep, self).run()
