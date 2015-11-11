from smartva import child_tariff_data
from smartva.tariff_prep import TariffPrep


class ChildTariff(TariffPrep):
    """Process Child VA Tariff data."""

    def __init__(self, working_dir_path, short_form, hce, free_text, malaria, country):
        super(ChildTariff, self).__init__(working_dir_path, short_form, hce, free_text, malaria, country)

        self.data_module = child_tariff_data

    def run(self):
        return super(ChildTariff, self).run()

    def _matches_undetermined_cause(self, va, u_row):
        va_age, u_age = float(va.age), float(u_row['age'])

        return ((u_age == 0.0 and va_age < 1.0) or
                (u_age == 1.0 and 1.0 <= va_age < 5.0) or
                (u_age == 5.0 and 5.0 <= va_age < 9.0) or
                (u_age == 10.0 and 10.0 <= va_age < 15.0))
