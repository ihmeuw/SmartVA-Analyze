from smartva.data import child_symptom_data
from smartva.symptom_prep import SymptomPrep


class ChildSymptomPrep(SymptomPrep):
    """Process Child VA Symptom data."""

    def __init__(self, working_dir_path, short_form):
        super(ChildSymptomPrep, self).__init__(working_dir_path, short_form)

        self.data_module = child_symptom_data

    def run(self):
        return super(ChildSymptomPrep, self).run()
