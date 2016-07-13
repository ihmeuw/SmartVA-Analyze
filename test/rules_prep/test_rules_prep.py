import csv
import os
import pytest
import shutil
import subprocess

import smartva.rules_prep
from . import always_false, always_true, conditional, sometimes_true

path = os.path.dirname(os.path.abspath(__file__))


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

    validate_matrix(iter(actual_results), iter(get_expected_results(local_file('none-logic-rules.csv'))))


@pytest.fixture
def input_file(tmpdir):
    dest = tmpdir.mkdir('intermediate-files').join('none-presymptom.csv')
    shutil.copy(local_file('none-presymptom.csv'), dest.strpath)
    return dest


RulesPrep = smartva.rules_prep.RulesPrep
all_rules = [conditional, sometimes_true, always_false, always_true]


@pytest.fixture
def prep(tmpdir):
    return RulesPrep(working_dir_path=tmpdir.strpath, short_form=True)


class TestRulesPrep(object):
    def test_instance(self, prep):
        assert isinstance(prep, RulesPrep)

    def test_run(self, prep, input_file, tmpdir):
        # subprocess.call(['open', prep.output_dir_path])
        prep.RULES = all_rules
        prep.run()

        validate_predictions(tmpdir.join('intermediate-files', 'none-logic-rules.csv'))
