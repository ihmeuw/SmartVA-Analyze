from smartva.rules import anemia
from smartva.data.constants import *

BASE_ROW = {
    'g5_02': FEMALE,
    'g5_04a': 13.0,
    'a3_07': YES,
    'a3_08': 91.0,
    'a3_10': YES,
    'a3_17': YES,
    'a3_18': YES,
    'a2_20': YES,
    'a2_37': YES,
    'a2_40': YES,
    'a2_43': YES,
    'a2_69': YES,
}


def test_logic_pass():
    assert anemia.logic_rule(BASE_ROW) == anemia.CAUSE_ID


def test_logic_fail_age():
    row = BASE_ROW.copy()
    row.update({
        'g5_04a': 12.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_gender():
    row = BASE_ROW.copy()
    row.update({
        'g5_02': YES,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_pregnant():
    row = BASE_ROW.copy()
    row.update({
        'a3_10': NO,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_period1():
    row = BASE_ROW.copy()
    row.update({
        'a3_07': NO,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_period2():
    row = BASE_ROW.copy()
    row.update({
        'a3_08': 90.0,
    })

    assert anemia.logic_rule(row) is False


def test_logic_pass_postpartum1():
    row = BASE_ROW.copy()
    row.update({
        'a3_17': YES,
        'a3_18': NO,
    })

    assert anemia.logic_rule(row) == anemia.CAUSE_ID


def test_logic_pass_postpartum2():
    row = BASE_ROW.copy()
    row.update({
        'a3_17': NO,
        'a3_18': YES,
    })

    assert anemia.logic_rule(row) == anemia.CAUSE_ID


def test_logic_fail_postpartum1():
    row = BASE_ROW.copy()
    row.update({
        'a3_17': NO,
        'a3_18': NO,
    })

    assert anemia.logic_rule(row) is False


def test_logic_pass_symptoms1():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': YES,
        'a2_37': YES,
        'a2_40': NO,
        'a2_43': YES,
        'a2_69': NO,
    })

    assert anemia.logic_rule(row) == anemia.CAUSE_ID


def test_logic_fail_symptoms1():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': NO,
        'a2_37': NO,
        'a2_40': NO,
        'a2_43': NO,
        'a2_69': NO,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_symptoms2():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': YES,
        'a2_37': NO,
        'a2_40': NO,
        'a2_43': NO,
        'a2_69': NO,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_symptoms3():
    row = BASE_ROW.copy()
    row.update({
        'a2_20': YES,
        'a2_37': YES,
        'a2_40': NO,
        'a2_43': NO,
        'a2_69': NO,
    })

    assert anemia.logic_rule(row) is False
