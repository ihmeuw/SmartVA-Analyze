import csv

import pytest

from smartva.symptom_prep import SymptomPrep
from smartva.data import child_symptom_data

headers = ['sid']
# Rash variables
headers.extend(['c4_31_1', 'c4_32', 'c4_33'])
headers.extend(['c1_22a'])
headers.extend(['c4_07b'])

data = [
    {'sid': 'multiple_stools', 'c4_07b': 2}, # two loose stools
    # The method which checks loose stool will throw a value error
    # if c4_07b is not in each row as a number (not string)
    # The value needs to be larger than 2 to pass the broken test
    {'sid': 'rash1', 'c4_31_1': '1', 'c4_32': '0', 'c4_33': '10.0', 'c4_07b': 9 },
    {'sid': 'hosp_death_5', 'c1_22a': '5', 'c4_07b': 9},
]

expected_results = [
    {'sid': 'multiple_stools', 's116991': '1'},
    {'sid': 'rash1', 's139991': '1', 's141991': '0'},
    {'sid': 'hosp_death_5', 's30991': '1'},
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('child-logic-rules.csv')
    with f_path.open('wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(data)
    return f_path


@pytest.fixture
def output_file(tmpdir):
    f_path = tmpdir.join('intermediate-files', 'child-symptom.csv')
    return f_path


@pytest.fixture
def prep(tmpdir):
    return SymptomPrep(child_symptom_data, tmpdir.strpath, True)


class TestChildSymptomPrep(object):
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
            v = v_matrix.next()
            for var in v:
                assert t[var] == v[var], "SID: '{}' does not produce expected result".format(t['sid'])
