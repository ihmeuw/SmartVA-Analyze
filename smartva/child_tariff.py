from smartva.data import child_tariff_data
from smartva.tariff_prep import TariffPrep


class ChildTariff(TariffPrep):
    """Process Child VA Tariff data."""

    def __init__(self, working_dir_path, short_form, options, country):
        super(ChildTariff, self).__init__(working_dir_path, short_form, options, country)

        self.data_module = child_tariff_data

    def run(self):
        return super(ChildTariff, self).run()

    def _calc_age_bin(self, age):
        age = float(age)
        # Age may have been filled with the default value of zero
        # In this case do not return an age value. When looking up
        # redistribution weights, the lookup should fail and default all-age
        # both-sex category will be used instead.
        if 28 / 365.0 < age < 12:
            return 1 if 1.0 <= age < 5 else int(age / 5) * 5
