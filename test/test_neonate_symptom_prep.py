import csv

import pytest

from smartva.symptom_prep import SymptomPrep
from smartva.data import neonate_symptom_data

headers = ['sid']
headers.extend(['c1_22a'])

data = [
    {'sid': 'hosp_death_5', 'c1_22a': '5'},
]

expected_results = [
    {'sid': 'hosp_death_5', 's30991': '1'},
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('neonate-logic-rules.csv')
    with f_path.open('wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(data)
    return f_path


@pytest.fixture
def output_file(tmpdir):
    f_path = tmpdir.join('intermediate-files', 'neonate-symptom.csv')
    return f_path


@pytest.fixture
def prep(tmpdir):
    return SymptomPrep(neonate_symptom_data, tmpdir.strpath, True, who_2016=True)


class TestNeonateSymptomPrep(object):
    def test_input_data(self, prep, input_file, output_file):
        print(input_file)
        prep.run()
        assert output_file.check()
        with output_file.open('rb') as f:
            r = csv.DictReader(f)
            matrix = [row for row in r]

        self.validate_matrix(iter(matrix), iter(expected_results))

    def validate_matrix(self, t_matrix, v_matrix):
        for t in t_matrix:
            v = next(v_matrix)
            for var in v:
                assert t[var] == v[var], "SID: '{}' does not produce expected result".format(t['sid'])
