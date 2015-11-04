from __future__ import print_function

from smartva import adult_symptom_data
from smartva.symptom_prep import SymptomPrep


class AdultSymptomPrep(SymptomPrep):
    """
    Prepare symptom data for tariff processing.

    The main goal of this step is to complete the conversion of symptom answers to binary data.

    Notes:
    Change sex from female = 2, male = 1 to female = 1, male = 0
    Unknown sex will default to 0 so it contributes nothing to the tariff score as calculated in the
    tariff 2.0 algorithm.

    For all indicators for different questions about injuries (road traffic, fall, fires) We only want
    to give a VA a 1 (yes) response for that question if the injury occurred within 30 days of death
    (i.e. s163<=30) Otherwise, we could have people who responded that they were in a car accident 20
    years prior to death be assigned to road traffic deaths.
    """

    def __init__(self, input_file, output_dir, short_form):
        super(AdultSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = adult_symptom_data

        self._init_data_module()

    def run(self):
        super(AdultSymptomPrep, self).run()
