from smartva.rules import other_pregnancy
from smartva.data.constants import *


def test_logic_pass_abortion():
    row = {
        SEX: FEMALE,
        AGE: 13.0,
        Adult.DURING_ABORTION: YES,
        Adult.LABOR_HOURS: 13.0,
    }

    assert other_pregnancy.logic_rule(row) is True


def test_logic_pass_childbirth():
    row = {
        SEX: FEMALE,
        AGE: 13.0,
        Adult.DURING_CHILDBIRTH: YES,
        Adult.LABOR_HOURS: 13.0,
    }

    assert other_pregnancy.logic_rule(row) is True


def test_logic_fail_sex():
    row = {
        SEX: MALE,
        AGE: 13.0,
        Adult.DURING_CHILDBIRTH: YES,
        Adult.LABOR_HOURS: 13.0,
    }

    assert other_pregnancy.logic_rule(row) is False


def test_logic_fail_age1():
    row = {
        SEX: FEMALE,
        AGE: 12.0,
        Adult.DURING_CHILDBIRTH: YES,
        Adult.LABOR_HOURS: 13.0,
    }

    assert other_pregnancy.logic_rule(row) is False


def test_logic_fail_age2():
    row = {
        SEX: FEMALE,
        AGE: 50.0,
        Adult.DURING_CHILDBIRTH: YES,
        Adult.LABOR_HOURS: 13.0,
    }

    assert other_pregnancy.logic_rule(row) is False


def test_logic_fail_labor_hours():
    row = {
        SEX: FEMALE,
        AGE: 13.0,
        Adult.DURING_CHILDBIRTH: YES,
        Adult.LABOR_HOURS: 12.0,
    }

    assert other_pregnancy.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert other_pregnancy.logic_rule(row) is False
