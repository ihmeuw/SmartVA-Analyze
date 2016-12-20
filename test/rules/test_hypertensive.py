import pytest
from smartva.rules import hypertensive
from smartva.data.constants import *

BASE_ROW = {
    SEX: FEMALE,
    AGE: 12.0,
    Adult.PERIOD_OVERDUE: NO,
    Adult.PERIOD_OVERDUE_DAYS: 0.0,
    Adult.PREGNANT: NO,
    Adult.CONVULSIONS: NO,
    Adult.EPILEPSY: NO,
}


def test_logic_fail_age_min():
    row = BASE_ROW.copy()
    row.update({
        Adult.PREGNANT: YES,
        Adult.CONVULSIONS: YES,
    })

    assert hypertensive.logic_rule(row) is False


def test_logic_fail_age_max():
    row = BASE_ROW.copy()
    row.update({
        AGE: 50,
        Adult.PREGNANT: YES,
    })

    assert hypertensive.logic_rule(row) is False


def test_logic_fail_gender():
    row = BASE_ROW.copy()
    row.update({
        SEX: MALE,
        AGE: 13.0,
        Adult.PREGNANT: YES,
    })

    assert hypertensive.logic_rule(row) is False


def test_logic_fail_period():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PERIOD_OVERDUE: YES,
        Adult.PERIOD_OVERDUE_DAYS: 90.0,
    })

    assert hypertensive.logic_rule(row) is False


@pytest.mark.xfail
def test_logic_pass_convulsions():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.CONVULSIONS: YES,
    })

    assert hypertensive.logic_rule(row) is True


@pytest.mark.xfail
def test_logic_fail_non_epileptic():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.CONVULSIONS: YES,
        Adult.EPILEPSY: YES,
    })

    assert hypertensive.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert hypertensive.logic_rule(row) is False
