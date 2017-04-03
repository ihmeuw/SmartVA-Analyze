from smartva.data import neonate_tariff_data
from smartva.tariff_prep import TariffPrep


class NeonateTariff(TariffPrep):
    """Process Neonate VA Tariff data."""

    def __init__(self, working_dir_path, short_form, options, country):
        super(NeonateTariff, self).__init__(working_dir_path, short_form, options, country)

        self.data_module = neonate_tariff_data

    def run(self):
        return super(NeonateTariff, self).run()

    def _calc_age_bin(self, age):
        if age <= 28:
            return 0 if float(age) < 7.0 else 7
