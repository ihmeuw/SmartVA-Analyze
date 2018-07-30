import csv
import os
import shutil

import pandas as pd
import numpy as np
import pytest

from smartva.tariff_prep import Record
from smartva import config
from smartva.tariff_prep import TariffPrep, get_tariff_matrix
from smartva.data import adult_tariff_data

path = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def input_file(tmpdir):
    dest = tmpdir.mkdir('intermediate-files').join('adult-symptom.csv')
    shutil.copy(local_file('adult-symptom.csv'), dest.strpath)
    return dest


@pytest.fixture
def prep(tmpdir):
    return TariffPrep(
        adult_tariff_data,
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country='USA'
    )


def local_file(filename):
    return os.path.join(path, filename)


def get_expected_results(file_):
    with open(file_, 'rb') as f:
        r = csv.DictReader(f)
        return [row for row in r]


def validate_matrix(actual, expected):
    for a in actual:
        e = expected.next()
        for var in e:
            assert a[var] == e[var], "SID: '{}' does not produce expected result".format(a['sid'])


def validate_predictions(file_):
    assert file_.check()
    with file_.open('rb') as f:
        r = csv.DictReader(f)
        actual_results = [row for row in r]

    validate_matrix(iter(actual_results), iter(get_expected_results(local_file('adult-predictions.csv'))))


@pytest.mark.skipif(os.environ.get('SKIP_FUNCTIONAL', 'false').lower() == 'true', reason='Skipping functional test.')
def test_tariff_prep(prep, input_file, tmpdir):
    prep.run()

    validate_predictions(tmpdir.join('adult-predictions.csv'))


def test_uniform_frequencies(prep):
    df = pd.read_csv(prep.validated_filename, index_col=0)
    df = df.loc[np.repeat(*zip(*prep.data_module.FREQUENCIES.items()))]
    counts = df.gs_text46.value_counts()
    assert len(counts.unique()) == 1


@pytest.mark.parametrize('age,expected', [
    (0, None),
    (12, 10),
    (15, 15),
    (34.5, 30),
    (57, 55),
    (65, 65),
    (97, 80),
])
def test_calc_age_bin(prep, age, expected):
    age_bin = prep._calc_age_bin(age)
    assert age_bin == expected


@pytest.mark.parametrize('malaria', [True, False])
@pytest.mark.parametrize('hiv', [True, False])
def test_csmf_summed_to_one(prep, malaria, hiv):
    prep.malaria_region = malaria
    prep.hiv_region = hiv
    causes = prep.data_module.CAUSES.values()

    user_data = [Record('sid{}'.format(i), age=35, sex=i % 2 + 1, cause=cause)
                 for i in range(7) for cause in causes]

    undetermined_weights = prep._get_undetermined_matrix()
    csmf, csmf_by_sex = prep.calculate_csmf(user_data, undetermined_weights)

    assert np.allclose(sum(csmf.values()), 1)
    for sex, csmf_data in csmf_by_sex.items():
        assert np.allclose(sum(csmf_data.values()), 1)


def test_injuries_have_no_positive_scores(tmpdir, prep):
    """
    All tariffs scores for injury causes should be negative or zero. Injuries
    should only be predicted from logic rules, not tariffs.
    """
    injuries = [5, 15, 18, 19, 21, 34, 38, 41, 45]

    tariffs_path = os.path.join(config.basedir, 'data', 'tariffs-adult.csv')
    with open(tariffs_path, 'r') as f:
        symptoms = next(csv.reader(f))
    symptoms.remove('xs_name')

    # Single row with every symptom endorsed
    row = {'sid': 'x'}
    row.update({symp: 1 for symp in symptoms})

    tariffs = get_tariff_matrix(tariffs_path, ['xs_name'],
                                prep.data_module.SPURIOUS_ASSOCIATIONS,
                                len(symptoms))

    scored = prep.score_symptom_data([row], tariffs)

    assert all([score <= 0 for cause, score in scored[0].scores.items()
                if cause in injuries])


def test_csmf_sex_undetermined_unknown_age(prep):
    """
    Redistributed CSMFs for undetermined causes of death should not include
    biologically impossible causes for males and females.
    """
    male_drops = []
    female_drops = []

    # remove sex specific drops
    male_drops.extend(prep.data_module.FEMALE_CAUSES)
    male_drops.extend(prep.data_module.MATERNAL_CAUSES)
    female_drops.extend(prep.data_module.MALE_CAUSES)

    # male and female user data with undetermined cause and age zero (unknown age)
    user_data_male = [Record('sid{}'.format(i), age=0, sex=1, cause34_name='Undetermined')
                        for i in range(7)]
    user_data_female = [Record('sid{}'.format(i), age=0, sex=2, cause34_name='Undetermined')
                        for i in range(7)]
    user_data_unknown = [Record('sid{}'.format(i), age=0, sex=0, cause34_name='Undetermined')
                        for i in range(7)]

    user_data = user_data_male + user_data_female + user_data_unknown

    undetermined_weights = prep._get_undetermined_matrix()
    csmf, csmf_by_sex = prep.calculate_csmf(user_data, undetermined_weights)

    for sex, csmf_data in csmf_by_sex.items():
        # check female causes not in male csmfs and vice versa
        if sex == 1:
            assert len(list(set(csmf_data.keys()) & set(male_drops))) == 0
        if sex == 2:
            assert len(list(set(csmf_data.keys()) & set(female_drops))) == 0
