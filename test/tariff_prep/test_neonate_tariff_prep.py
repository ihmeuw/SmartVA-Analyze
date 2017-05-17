import csv
import os
import shutil

import pandas as pd
import numpy as np
import pytest

from smartva.neonate_tariff import NeonateTariff

path = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def input_file(tmpdir):
    dest = tmpdir.mkdir('intermediate-files').join('neonate-symptom.csv')
    shutil.copy(local_file('neonate-symptom.csv'), dest.strpath)
    return dest


@pytest.fixture
def prep(tmpdir):
    return NeonateTariff(
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True},
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

    validate_matrix(iter(actual_results), iter(get_expected_results(local_file('neonate-predictions.csv'))))


@pytest.mark.skipif(os.environ.get('SKIP_FUNCTIONAL', 'false').lower() == 'true', reason='Skipping functional test.')
def test_tariff_prep(prep, input_file, tmpdir):
    prep.run()

    validate_predictions(tmpdir.join('neonate-predictions.csv'))


def test_uniform_frequencies(prep):
    df = pd.read_csv(prep.va_validated_filename, index_col=0)
    df = df.loc[np.repeat(*zip(*prep.data_module.FREQUENCIES.items()))]

    # Neonates use the six causes in the 34 cause list
    counts = df.gs_text34.value_counts()
    assert len(counts.unique()) == 1


@pytest.mark.parametrize('age,expected', [
    (0, 0),
    (4.5, 0),
    (7, 7),
    (15, 7),
    (28, 7),
    (29, None),
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
    cause_counts = dict(zip(causes, [7 for c in causes]))
    prep.write_csmf(cause_counts)

    outfile_path = os.path.join(prep.output_dir_path,
                                '{}-csmf.csv'.format(prep.AGE_GROUP))
    csmf = pd.read_csv(outfile_path)
    assert np.allclose(csmf.CSMF.sum(), 1)
