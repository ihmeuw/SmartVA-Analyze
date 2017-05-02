import csv
import os
import pytest
import shutil
import subprocess

import smartva.rules_prep
from smartva.rules import (
    aids_child,
    bite_adult,
    bite_child,
    cvd_child,
    drowning_adult,
    drowning_child,
    falls_adult,
    falls_child,
    fires_adult,
    fires_child,
    homicide_adult,
    homicide_child,
    other_injury_adult,
    other_injury_child,
    poisoning_adult,
    poisoning_child,
    road_traffic_adult,
    road_traffic_child,
    stillbirth,
    stroke,
    suicide,
)

import always_exception
import always_false
import always_true
import conditional
import sometimes_true

import smartva.data.adult_tariff_data as adult_tariff_data
import smartva.data.child_tariff_data as child_tariff_data
import smartva.data.neonate_tariff_data as neonate_tariff_data

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

@pytest.mark.parametrize('rule_list',[
        [always_true, conditional],
        [conditional, always_true],
    ])
def test_rule_order(tmpdir, rule_list):
    intermediate = tmpdir.mkdir('intermediate-files')
    input_file = intermediate.join('none-presymptom.csv')
    input_file.write('sid,condition\nfoo,1')

    prep = RulesPrep(working_dir_path=tmpdir.strpath, short_form=True,
                     age_group='none', rules=rule_list)
    prep.run()

    output_file = os.path.join(intermediate.strpath, 'none-logic-rules.csv')
    with open(output_file, 'r') as f:
        for row in csv.DictReader(f):
            assert int(row['cause']) == rule_list[0].CAUSE_ID


class TestAdultRulesPrep(object):
    RULE_LIST = [
        road_traffic_adult,
        bite_adult,
        drowning_adult,
        fires_adult,
        falls_adult,
        poisoning_adult,
        other_injury_adult,
        homicide_adult,
        suicide,
        stroke,
    ]

    def test_instance(self, tmpdir):
        adult_rules_prep = smartva.rules_prep.AdultRulesPrep(working_dir_path=tmpdir.strpath, short_form=True)

        assert adult_rules_prep.AGE_GROUP == 'adult'
        assert adult_rules_prep.rules == self.RULE_LIST

    @pytest.mark.parametrize("rule", RULE_LIST)
    def test_prediction_exists(self, rule):
        assert rule.CAUSE_ID in adult_tariff_data.CAUSES46
        assert rule.CAUSE_ID in adult_tariff_data.CAUSE_REDUCTION
        reduced_cause = adult_tariff_data.CAUSE_REDUCTION.get(rule.CAUSE_ID)
        assert reduced_cause in adult_tariff_data.CAUSES


class TestChildRulesPrep(object):
    RULE_LIST = [
        road_traffic_child,
        bite_child,
        drowning_child,
        fires_child,
        falls_child,
        poisoning_child,
        other_injury_child,
        homicide_child,
        cvd_child,
        aids_child,
    ]

    def test_instance(self, tmpdir):
        rules_prep = smartva.rules_prep.ChildRulesPrep(working_dir_path=tmpdir.strpath, short_form=True)

        assert rules_prep.AGE_GROUP == 'child'
        assert rules_prep.rules == self.RULE_LIST

    @pytest.mark.parametrize("rule", RULE_LIST)
    def test_prediction_exists(self, rule):
        assert rule.CAUSE_ID in child_tariff_data.CAUSES46
        assert rule.CAUSE_ID in child_tariff_data.CAUSE_REDUCTION
        reduced_cause = child_tariff_data.CAUSE_REDUCTION.get(rule.CAUSE_ID)
        assert reduced_cause in child_tariff_data.CAUSES


class TestNeonateRulesPrep(object):
    RULE_LIST = [
        stillbirth,
    ]

    def test_instance(self, tmpdir):
        rules_prep = smartva.rules_prep.NeonateRulesPrep(working_dir_path=tmpdir.strpath, short_form=True)

        assert rules_prep.AGE_GROUP == 'neonate'
        assert rules_prep.rules == self.RULE_LIST

    @pytest.mark.parametrize("rule", RULE_LIST)
    def test_prediction_exists(self, rule):
        assert rule.CAUSE_ID in neonate_tariff_data.CAUSES46
        assert rule.CAUSE_ID in neonate_tariff_data.CAUSE_REDUCTION
        reduced_cause = neonate_tariff_data.CAUSE_REDUCTION.get(rule.CAUSE_ID)
        assert reduced_cause in neonate_tariff_data.CAUSES
