from smartva import neonate_tariff_data
from smartva.tariff_prep import TariffPrep


class NeonateTariff(TariffPrep):
    """Process Neonate VA Tariff data."""

    def __init__(self, input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form):
        super(NeonateTariff, self).__init__(input_file, output_dir, intermediate_dir, hce, free_text, malaria, country, short_form)
        self.data_module = neonate_tariff_data

        self._init_data_module()

    def run(self):
        super(NeonateTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = map(float, [va.age, u_row['age']])

        return ((u_age == 0.0 and va_age < 7.0) or
                (u_age == 7.0 and 7.0 <= va_age < 28.0))
