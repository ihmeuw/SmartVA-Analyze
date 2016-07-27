import csv
import os
import pytest
import shutil
import subprocess

import smartva.rules_prep
from smartva.rules import *

import always_exception
import always_false
import always_true
import conditional
import sometimes_true

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
all_rules = [always_exception, conditional, sometimes_true, always_false, always_true]


@pytest.fixture
def prep(tmpdir):
    return RulesPrep(working_dir_path=tmpdir.strpath, short_form=True, age_group='none', rules=all_rules)


class TestRulesPrep(object):
    def test_instance(self, prep):
        assert isinstance(prep, RulesPrep)

    def test_run(self, prep, input_file, tmpdir):
        # subprocess.call(['open', prep.output_dir_path])
        prep.run()

        validate_predictions(tmpdir.join('intermediate-files', 'none-logic-rules.csv'))


class TestAdultRulesPrep(object):
    def test_instance(self, tmpdir):
        adult_rules_prep = smartva.rules_prep.AdultRulesPrep(working_dir_path=tmpdir.strpath, short_form=True)

        assert adult_rules_prep.AGE_GROUP == 'adult'
        assert adult_rules_prep.rules == [
            anemia,
            bite_adult,
            drowning_adult,
            falls_adult,
            fires_adult,
            hemorrhage,
            homicide_adult,
            hypertensive,
            other_injury_adult,
            other_pregnancy,
            poisoning_adult,
            road_traffic_adult,
            sepsis,
            suicide,
        ]


class TestChildRulesPrep(object):
    def test_instance(self, tmpdir):
        rules_prep = smartva.rules_prep.ChildRulesPrep(working_dir_path=tmpdir.strpath, short_form=True)

        assert rules_prep.AGE_GROUP == 'child'
        assert rules_prep.rules == [
            bite_child,
            cancer_child,
            drowning_child,
            falls_child,
            fires_child,
            homicide_child,
            other_injury_child,
            poisoning_child,
            road_traffic_child,
        ]


class TestNeonateRulesPrep(object):
    def test_instance(self, tmpdir):
        rules_prep = smartva.rules_prep.NeonateRulesPrep(working_dir_path=tmpdir.strpath, short_form=True)

        assert rules_prep.AGE_GROUP == 'neonate'
        assert rules_prep.rules == [
            stillbirth,
            tetanus_neonate,
        ]
