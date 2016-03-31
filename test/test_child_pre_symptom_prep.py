import csv

import pytest

from smartva.child_pre_symptom_prep import ChildPreSymptomPrep

headers = ['sid']
# Rash variables
headers.extend(['child_4_30', 'child_4_31', 'child_4_32', 'child_4_33', 'child_4_33a'])
# Free text variables
headers.extend(['child_1_19a', 'child_3_3a', 'child_5_0b', 'child_5_9', 'child_5_12', 'child_5_13', 'child_5_14', 'child_5_15', 'child_5_16', 'child_6_c'])
headers.extend(['child_1_15', 'child_1_18', 'child_3_2', 'child_5_4', 'child_5_5', 'child_5_10', 'child_5_11'])
headers.extend(['child_6_1'])

data = [
    {'sid': 'rash1', 'child_4_30': '1', 'child_4_31': '1 2 3', 'child_4_32': '2', 'child_4_33': '4', 'child_4_33a': '10'},
    {'sid': 'freetext_1_19a', 'child_1_15': 1, 'child_1_18': 1, 'child_1_19a': 'malaria'},
    {'sid': 'freetext_3_3a', 'child_3_2': 1, 'child_3_3a': 'malaria'},
    {'sid': 'freetext_5_0b', 'child_5_0b': 'malaria'},  # validation: child_5_4,5=1?
    {'sid': 'freetext_5_9', 'child_5_4': 1, 'child_5_5': 1, 'child_5_9': 'malaria'},
    {'sid': 'freetext_5_12', 'child_5_10': 1, 'child_5_11': 1, 'child_5_12': 'malaria'},
    {'sid': 'freetext_5_13', 'child_5_10': 1, 'child_5_11': 1, 'child_5_13': 'malaria'},
    {'sid': 'freetext_5_14', 'child_5_10': 1, 'child_5_11': 1, 'child_5_14': 'malaria'},
    {'sid': 'freetext_5_15', 'child_5_10': 1, 'child_5_11': 1, 'child_5_15': 'malaria'},
    {'sid': 'freetext_5_16', 'child_5_10': 1, 'child_5_11': 1, 'child_5_16': 'malaria'},
    {'sid': 'freetext_6_c', 'child_6_c': 'malaria'},
    {'sid': 'freetext_6_1', 'child_6_1': '1'}
]

expected_results = [
    {'sid': 'rash1', 'c4_31_1': '1', 'c4_32': '0', 'c4_33': '10.0'},
    {'sid': 'freetext_1_19a', 's999930': '1'},
    {'sid': 'freetext_3_3a', 's999930': '1'},
    {'sid': 'freetext_5_0b', 's999930': '1'},
    {'sid': 'freetext_5_9', 's999930': '1'},
    {'sid': 'freetext_5_12', 's999930': '1'},
    {'sid': 'freetext_5_13', 's999930': '1'},
    {'sid': 'freetext_5_14', 's999930': '1'},
    {'sid': 'freetext_5_15', 's999930': '1'},
    {'sid': 'freetext_5_16', 's999930': '1'},
    {'sid': 'freetext_6_c', 's999930': '1'},
    {'sid': 'freetext_6_1', 'c_6_1': '1', 's99991': '1'},
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('child-prepped.csv')
    with f_path.open('wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(data)
    return f_path


@pytest.fixture
def output_file(tmpdir):
    f_path = tmpdir.join('intermediate-files', 'child-presymptom.csv')
    return f_path


@pytest.fixture
def prep(tmpdir):
    return ChildPreSymptomPrep(tmpdir.strpath, True)


class TestChildPreSymptomPrep(object):
    def test_fix_rash_location(self, prep):
        row = {
            'c4_31_1': '1 2 3',
            'c4_32': '',
        }

        prep.fix_rash_location(row)

        assert (row == {'c4_31_1': 1, 'c4_32': 0})

    def test_recodes(self, prep):
        row = dict(sid='', c1_22a=4)
        prep.recode_answers(row, prep.data_module.RECODE_MAP)
        assert row == dict(sid='', c1_22a=4)

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
