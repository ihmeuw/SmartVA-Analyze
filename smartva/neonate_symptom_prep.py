from smartva.data import neonate_symptom_data
from smartva.symptom_prep import SymptomPrep


class NeonateSymptomPrep(SymptomPrep):
    """Process Neonate VA Symptom data."""

    def __init__(self, working_dir_path, short_form):
        super(NeonateSymptomPrep, self).__init__(working_dir_path, short_form)

        self.data_module = neonate_symptom_data

    def run(self):
        return super(NeonateSymptomPrep, self).run()
