from smartva import adult_symptom_data
from smartva.symptom_prep import SymptomPrep


class AdultSymptomPrep(SymptomPrep):
    """Process Adult VA Symptom data."""

    def __init__(self, input_file, output_dir, short_form):
        super(AdultSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = adult_symptom_data

        self._init_data_module()

    def run(self):
        super(AdultSymptomPrep, self).run()
