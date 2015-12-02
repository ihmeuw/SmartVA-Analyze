from smartva.data import neonate_pre_symptom_data
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.utils.conversion_utils import value_or_default


class NeonatePreSymptomPrep(PreSymptomPrep):
    """Process Neonate VA Pre-Symptom data."""

    def __init__(self, working_dir_path, short_form):
        PreSymptomPrep.__init__(self, working_dir_path, short_form)

        self.data_module = neonate_pre_symptom_data

    def run(self):
        return super(NeonatePreSymptomPrep, self).run()

    def pre_processing_step(self, row):
        self.fix_agedays(row)
        self.calculate_age_at_death_value(row)

    def fix_agedays(self, row):
        """Fix child agedays.  If it's blank give it a 0, if it's not, give it a 4.

        Args:
            row (dict): Row of VA data.
        """
        value = value_or_default(row['c1_25b'], int, default=None)
        if value is None:
            row['c1_25a'] = 0
        else:
            row['c1_25a'] = 4

    def calculate_age_at_death_value(self, row):
        """Write age at death value to the appropriate variable.

        Args:
            row (dict): Row of VA data.
        """
        value = value_or_default(row['c1_25b'], int, default=None)
        if 1 <= value <= 28:
            row['c1_26'] = 1

    def post_processing_step(self, row):
        self.process_weight_sd_vars(row, self.data_module.EXAM_DATE_VARS, self.data_module.WEIGHT_SD_DATA)
