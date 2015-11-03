import csv

from smartva import neonate_symptom_data
from smartva.neonate_symptom_data import (
    GENERATED_VARS_DATA,
    VAR_CONVERSION_MAP,
    DURATION_CUTOFF_DATA,
    INJURY_VARS,
    BINARY_VARS,
    AGE_QUARTILE_BINARY_VARS,
    BINARY_CONVERSION_MAP,
    COPY_VARS
)
from smartva.symptom_prep import SymptomPrep
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import additional_headers_and_values


class NeonateSymptomPrep(SymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        super(NeonateSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.AGE_GROUP = 'neonate'

        self.data_module = neonate_symptom_data

        self._init_data_module()

    def run(self):
        super(NeonateSymptomPrep, self).run()
