from smartva import adult_pre_symptom_data
from smartva.pre_symptom_prep import PreSymptomPrep


class AdultPreSymptomPrep(PreSymptomPrep):
    """Process Adult VA Pre-Symptom data.

    Notes:
        Adult data does not require special pre/post-processing actions. """

    def __init__(self, working_dir_path, short_form):
        PreSymptomPrep.__init__(self, working_dir_path, short_form)

        self.data_module = adult_pre_symptom_data

    def run(self):
        return super(AdultPreSymptomPrep, self).run()

    def post_processing_step(self, row):
        pass

    def pre_processing_step(self, row):
        pass
