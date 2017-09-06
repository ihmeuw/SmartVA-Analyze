import csv


import pytest
import pandas as pd
import numpy as np

from smartva.data.countries import COUNTRIES, COUNTRY_DEFAULT
from smartva.adult_tariff import AdultTariff
from smartva.child_tariff import ChildTariff
from smartva.neonate_tariff import NeonateTariff


iso3s = [country.split(' ')[-1].strip('()') for country in COUNTRIES
         if country != COUNTRY_DEFAULT]
tariff_subclasses = [AdultTariff, ChildTariff, NeonateTariff]


@pytest.mark.parametrize('tariff', tariff_subclasses)
def test_redistribution_weights_sum_to_one(tmpdir, tariff):
    prep = tariff(
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country='USA'
    )
    df = pd.read_csv(prep.undetermined_matrix_filename)
    weights_by_id = df.groupby(['age', 'sex', 'iso3']).sum()
    assert weights_by_id.apply(np.allclose, args=(1,)).all()


@pytest.mark.skipif(not pytest.config.getoption("--data-checks"),
                    reason="need --data-checks option to run")
@pytest.mark.parametrize('tariff', tariff_subclasses)
@pytest.mark.parametrize('country', iso3s)
def test_redistribution_weights_for_countries(tmpdir, tariff, country):
    """Any valid country from the countries list should be present and contain
       the default key used for invalid age-sex observations."""
    prep = tariff(
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country=country
    )
    undetermined_weights = prep._get_undetermined_matrix()
    assert isinstance(undetermined_weights, dict)
    assert (99, 3) in undetermined_weights


@pytest.mark.parametrize('tariff', tariff_subclasses)
@pytest.mark.parametrize('short_form', [True, False])
@pytest.mark.parametrize('hce', [True, False])
def test_redistribution_weights(tmpdir, tariff, short_form, hce):
    """Verify the shape of structure of the redistribution weights is correct
       for one country."""
    prep = tariff(
        working_dir_path=tmpdir.strpath,
        short_form=short_form,
        options={'hce': hce, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country='USA'
    )
    undetermined_weights = prep._get_undetermined_matrix()

    cause_list = set(prep.data_module.CAUSES[cause]
                     for _, cause in prep.data_module.CAUSE_REDUCTION.items())
    for key, weights in undetermined_weights.items():
        age, sex = key
        assert sex in [1, 2, 3]
        if prep.AGE_GROUP == 'adult':
            assert age in range(10, 81, 5) + [99]
        elif prep.AGE_GROUP == 'child':
            assert age in [0, 1, 5, 10, 99]
        elif prep.AGE_GROUP == 'neonate':
            assert age in [0, 7, 99]

        assert not cause_list.symmetric_difference(weights.keys())
        assert np.allclose(sum(weights.values()), 1)


@pytest.mark.parametrize('tariff', tariff_subclasses)
def test_redistribution_weights_no_country(tmpdir, tariff):
    prep = tariff(
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country=None
    )
    undetermined_weights = prep._get_undetermined_matrix()
    assert undetermined_weights == {}


@pytest.mark.parametrize('tariff', tariff_subclasses)
def test_redistribution_causes_match_reporting_causes(tmpdir, tariff):
    prep = tariff(
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country=None
    )
    with open(prep.undetermined_matrix_filename) as f:
        undetermined_causes = {row['gs_text34'] for row in csv.DictReader(f)}

    tariff_causes = {prep.data_module.CAUSES[cause]
                     for cause in prep.data_module.CAUSE_REDUCTION.values()}

    assert undetermined_causes == tariff_causes
