from smartva.data import neonate_tariff_data
from smartva.tariff_prep import TariffPrep


class NeonateTariff(TariffPrep):
    """Process Neonate VA Tariff data."""

    def __init__(self, working_dir_path, short_form, options, country):
        super(NeonateTariff, self).__init__(working_dir_path, short_form, options, country)

        self.data_module = neonate_tariff_data
        self.tariff_matrix_filename = None # take the default
        self.va_validated_filename = None # take the default
        self.undetermined_matrix_filename = None # take the default

    def run(self):
        return super(NeonateTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = float(va.age), float(u_row['age'])

        return ((u_age == 0.0 and va_age < 7.0) or
                (u_age == 7.0 and 7.0 <= va_age < 28.0))
