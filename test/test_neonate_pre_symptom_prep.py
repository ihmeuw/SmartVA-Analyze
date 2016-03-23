import csv

import pytest

from smartva.neonate_pre_symptom_prep import NeonatePreSymptomPrep

headers = ['sid']
# Free text variables
headers.extend(['child_1_19a', 'child_3_3a', 'child_5_0b', 'child_5_9', 'child_5_12', 'child_5_13', 'child_5_14', 'child_5_15', 'child_5_16', 'child_6_c'])
headers.extend(['child_1_15', 'child_1_18'])
headers.extend(['child_3_2'])
headers.extend(['child_5_4', 'child_5_5'])
headers.extend(['child_5_10', 'child_5_11'])
headers.extend(['neonate_6_1'])
headers.extend(['child_3_11', 'child_3_12', 'child_3_13'])
headers.extend(['child_1_22'])

data = [
    {'sid': 'freetext_1_19a', 'child_1_15': 1, 'child_1_18': 1, 'child_1_19a': 'cry'},
    {'sid': 'freetext_3_3a', 'child_3_2': 1, 'child_3_3a': 'cry'},
    {'sid': 'freetext_5_0b', 'child_5_0b': 'cry'},  # validation: child_5_4,5=1?
    {'sid': 'freetext_5_9', 'child_5_4': 1, 'child_5_5': 1, 'child_5_9': 'cry'},
    {'sid': 'freetext_5_12', 'child_5_10': 1, 'child_5_11': 1, 'child_5_12': 'cry'},
    {'sid': 'freetext_5_13', 'child_5_10': 1, 'child_5_11': 1, 'child_5_13': 'cry'},
    {'sid': 'freetext_5_14', 'child_5_10': 1, 'child_5_11': 1, 'child_5_14': 'cry'},
    {'sid': 'freetext_5_15', 'child_5_10': 1, 'child_5_11': 1, 'child_5_15': 'cry'},
    {'sid': 'freetext_5_16', 'child_5_10': 1, 'child_5_11': 1, 'child_5_16': 'cry'},
    {'sid': 'freetext_6_c', 'child_6_c': 'cry'},
    {'sid': 'freetext_6_1', 'neonate_6_1': '1'},
    {'sid': 'c3_13_skipped', 'child_3_11': '1', 'child_3_12': '0', 'child_3_13': '1'},
    {'sid': 'not_in_hosp', 'child_1_22': '4'},
]

expected_results = [
    {'sid': 'freetext_1_19a', 's999910': '1'},
    {'sid': 'freetext_3_3a', 's999910': '1'},
    {'sid': 'freetext_5_0b', 's999910': '1'},
    {'sid': 'freetext_5_9', 's999910': '1'},
    {'sid': 'freetext_5_12', 's999910': '1'},
    {'sid': 'freetext_5_13', 's999910': '1'},
    {'sid': 'freetext_5_14', 's999910': '1'},
    {'sid': 'freetext_5_15', 's999910': '1'},
    {'sid': 'freetext_5_16', 's999910': '1'},
    {'sid': 'freetext_6_c', 's999910': '1'},
    {'sid': 'freetext_6_1', 'n_6_1': '1', 's99993': '1'},
    {'sid': 'c3_13_skipped', 'c3_13': '1'},
    {'sid': 'not_in_hosp', 'c1_22a': '4'}
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('neonate-prepped.csv')
    with f_path.open('wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(data)
    return f_path


@pytest.fixture
def output_file(tmpdir):
    f_path = tmpdir.join('intermediate-files', 'neonate-presymptom.csv')
    return f_path


@pytest.fixture
def prep(tmpdir):
    return NeonatePreSymptomPrep(tmpdir.strpath, True)


class TestNeonatePreSymptomPrep(object):
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
                assert t[var] == v[var]
