from __future__ import print_function

from smartva import child_tariff_data
from smartva.tariff_prep import TariffPrep


class ChildTariff(TariffPrep):
    def __init__(self, input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form):
        super(ChildTariff, self).__init__(input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form)
        self.data_module = child_tariff_data

        self._init_data_module()

    def run(self):
        return super(ChildTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = map(float, [va.age, u_row['age']])

        return ((u_age == 0.0 and va_age < 1.0) or
                (u_age == 1.0 and 1.0 <= va_age < 5.0) or
                (u_age == 5.0 and 5.0 <= va_age < 9.0) or
                (u_age == 10.0 and 10.0 <= va_age < 15.0))
