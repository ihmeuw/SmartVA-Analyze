from smartva.data import adult_symptom_data
from smartva.symptom_prep import SymptomPrep


class AdultSymptomPrep(SymptomPrep):
    """Process Adult VA Symptom data."""

    def __init__(self, working_dir_path, short_form):
        super(AdultSymptomPrep, self).__init__(working_dir_path, short_form)

        self.data_module = adult_symptom_data

    def run(self):
        return super(AdultSymptomPrep, self).run()
