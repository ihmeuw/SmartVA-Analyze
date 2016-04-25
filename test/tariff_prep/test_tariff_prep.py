import pytest
import os

from smartva.tariff_prep import TariffPrep, get_cause_num, exclude_spurious_associations

import sample_tariff_data


class TariffPrepMock(TariffPrep):
    def _matches_undetermined_cause(self, va, u_row):
        return True


@pytest.fixture
def prep():
    prep = TariffPrepMock('/', True, {'hce': True, 'free_text': True, 'hiv': True, 'malaria': True}, 'USA')
    prep.data_module = sample_tariff_data
    return prep


class TestTariffPrep:
    def test_class_members(self, prep):
        assert prep.hce
        assert prep.free_text
        assert prep.hiv_region
        assert prep.malaria_region
        assert prep.iso3 == 'USA'

        assert prep.cause_list == []

        assert prep.data_module == sample_tariff_data

        assert prep.AGE_GROUP == 'sample'
