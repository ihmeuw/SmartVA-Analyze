from smartva.data import adult_tariff_data
from smartva.tariff_prep import TariffPrep


class AdultTariff(TariffPrep):
    """Process Adult VA Tariff data."""

    def __init__(self, working_dir_path, short_form, options, country):
        super(AdultTariff, self).__init__(working_dir_path, short_form, options, country)

        self.data_module = adult_tariff_data
        self.tariff_matrix_filename = None # take the default
        self.va_validated_filename = None # take the default
        self.undetermined_matrix_filename = None # take the default

    def run(self):
        return super(AdultTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = float(va.age), float(u_row['age'])

        return ((va_age <= u_age < va_age + 5.0) or
                (u_age == 80.0 and va_age > 80.0))
