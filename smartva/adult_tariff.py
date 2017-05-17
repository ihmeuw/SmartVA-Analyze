from smartva.data import adult_tariff_data
from smartva.tariff_prep import TariffPrep


class AdultTariff(TariffPrep):
    """Process Adult VA Tariff data."""

    def __init__(self, working_dir_path, short_form, options, country):
        super(AdultTariff, self).__init__(working_dir_path, short_form, options, country)

        self.data_module = adult_tariff_data

    def run(self):
        return super(AdultTariff, self).run()

    def _calc_age_bin(self, age):
        age = float(age)
        # Age may have been filled with the default value of zero
        # In this case do not return an age value. When looking up
        # redistribution weights, the lookup should fail and default all-age
        # both-sex category will be used instead.
        if age >= 12:
            return int(age / 5) * 5 if age < 80 else 80
