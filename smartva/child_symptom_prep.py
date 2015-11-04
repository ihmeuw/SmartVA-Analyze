from smartva import child_symptom_data
from smartva.symptom_prep import SymptomPrep


class ChildSymptomPrep(SymptomPrep):
    """Process Child VA Symptom data."""

    def __init__(self, input_file, output_dir, short_form):
        super(ChildSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = child_symptom_data

        self._init_data_module()

    def run(self):
        super(ChildSymptomPrep, self).run()


