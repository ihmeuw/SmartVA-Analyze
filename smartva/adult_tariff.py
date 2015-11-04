from __future__ import print_function

from smartva import adult_tariff_data
from smartva.tariff_prep import TariffPrep


class AdultTariff(TariffPrep):
    def __init__(self, input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form):
        super(AdultTariff, self).__init__(input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form)
        self.data_module = adult_tariff_data

        self._init_data_module()

    def run(self):
        return super(AdultTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = map(float, [va.age, u_row['age']])

        return ((va_age <= u_age < va_age + 5.0) or
                (u_age == 80.0 and va_age > 80.0))
