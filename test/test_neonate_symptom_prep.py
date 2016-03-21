import csv

import pytest

from smartva.neonate_symptom_prep import NeonateSymptomPrep

headers = ['sid']

data = [
  
]

expected_results = [
  
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('neonate-presymptom.csv')
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
    return NeonateSymptomPrep(tmpdir.strpath, True)


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
            v = v_matrix.next()
            for var in v:
                assert t[var] == v[var]
