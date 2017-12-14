import csv

import pytest

from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.data import adult_pre_symptom_data

headers = ['sid']
# Free text variables
headers.extend(['adult_5_2a', 'adult_6_3b', 'adult_6_8', 'adult_6_11', 'adult_6_12', 'adult_6_13', 'adult_6_14', 'adult_6_15', 'adult_7_c'])
headers.extend(['adult_6_4', 'adult_6_5', 'adult_6_9', 'adult_6_10'])
headers.extend(['adult_7_1'])

data = [
    {'sid': 'freetext_5_2a', 'adult_5_2a': 'malaria'},
    {'sid': 'freetext_6_3b', 'adult_6_3b': 'malaria'},
    {'sid': 'freetext_6_8', 'adult_6_4': 1, 'adult_6_5': 1, 'adult_6_8': 'malaria'},
    {'sid': 'freetext_6_11', 'adult_6_9': 1, 'adult_6_10': 1, 'adult_6_11': 'malaria'},
    {'sid': 'freetext_6_12', 'adult_6_9': 1, 'adult_6_10': 1, 'adult_6_12': 'malaria'},
    {'sid': 'freetext_6_13', 'adult_6_9': 1, 'adult_6_10': 1, 'adult_6_13': 'malaria'},
    {'sid': 'freetext_6_14', 'adult_6_9': 1, 'adult_6_10': 1, 'adult_6_14': 'malaria'},
    {'sid': 'freetext_6_15', 'adult_6_9': 1, 'adult_6_10': 1, 'adult_6_15': 'malaria'},
    {'sid': 'freetext_7_c', 'adult_7_c': 'malaria'},
    {'sid': 'freetext_7_1', 'adult_7_1': '1'},
]

expected_results = [
    {'sid': 'freetext_5_2a', 's9999108': '1'},
    {'sid': 'freetext_6_3b', 's9999108': '1'},
    {'sid': 'freetext_6_8', 's9999108': '1'},
    {'sid': 'freetext_6_11', 's9999108': '1'},
    {'sid': 'freetext_6_12', 's9999108': '1'},
    {'sid': 'freetext_6_13', 's9999108': '1'},
    {'sid': 'freetext_6_14', 's9999108': '1'},
    {'sid': 'freetext_6_15', 's9999108': '1'},
    {'sid': 'freetext_7_c', 's9999108': '1'},
    {'sid': 'freetext_7_1', 'a_7_1': '1', 's999999': '1'},
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('adult-prepped.csv')
    with f_path.open('wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(data)
    return f_path


@pytest.fixture
def output_file(tmpdir):
    f_path = tmpdir.join('intermediate-files', 'adult-presymptom.csv')
    return f_path


@pytest.fixture
def prep(tmpdir):
    return PreSymptomPrep(adult_pre_symptom_data, tmpdir.strpath, True)


class TestAdultPreSymptomPrep(object):
    def test_input_data(self, prep, input_file, output_file):
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
