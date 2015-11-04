from smartva import adult_tariff_data
from smartva.tariff_prep import TariffPrep


class AdultTariff(TariffPrep):
    """Process Adult VA Tariff data."""

    def __init__(self, input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form):
        super(AdultTariff, self).__init__(input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form)
        self.data_module = adult_tariff_data

    def run(self):
        return super(AdultTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = float(va.age), float(u_row['age'])

        return ((va_age <= u_age < va_age + 5.0) or
                (u_age == 80.0 and va_age > 80.0))
