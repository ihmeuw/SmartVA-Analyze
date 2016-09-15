import pytest
from smartva.rules import hemorrhage
from smartva.data.constants import *

BASE_ROW = {
    SEX: FEMALE,
    AGE: 12.0,
    Adult.PERIOD_OVERDUE: NO,
    Adult.PERIOD_OVERDUE_DAYS: 0.0,
    Adult.PREGNANT: NO,
    Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: NO,
    Adult.DURING_ABORTION: NO,
    Adult.DURING_CHILDBIRTH: NO,
    Adult.EXCESSIVE_BLEEDING_DURING: NO,
    Adult.AFTER_ABORTION: NO,
    Adult.AFTER_CHILDBIRTH: NO,
    Adult.EXCESSIVE_BLEEDING_AFTER: NO,
}


def test_logic_fail_age_min():
    row = BASE_ROW.copy()
    row.update({
        Adult.PREGNANT: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is False


def test_logic_fail_age_max():
    row = BASE_ROW.copy()
    row.update({
        AGE: 50,
        Adult.PREGNANT: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is False


def test_logic_fail_gender():
    row = BASE_ROW.copy()
    row.update({
        SEX: MALE,
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is False


def test_logic_pass_period():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PERIOD_OVERDUE: YES,
        Adult.PERIOD_OVERDUE_DAYS: 91.0,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_logic_fail_period():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PERIOD_OVERDUE: YES,
        Adult.PERIOD_OVERDUE_DAYS: 90.0,
        Adult.PALE: YES,
        Adult.CHEST_PAIN: YES,
        Adult.HEADACHES: YES,
    })

    assert hemorrhage.logic_rule(row) is False


def test_logic_pass_during_abortion():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.DURING_ABORTION: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_logic_pass_during_childbirth():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.DURING_CHILDBIRTH: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_logic_pass_after_abortion():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.AFTER_ABORTION: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_logic_pass_after_childbirth():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.AFTER_CHILDBIRTH: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_logic_pass_bleeding_prior():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_logic_pass_bleeding_during():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.EXCESSIVE_BLEEDING_DURING: YES,
    })

    assert hemorrhage.logic_rule(row) is True

@pytest.mark.xfail
def test_logic_pass_bleeding_after():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.EXCESSIVE_BLEEDING_AFTER: YES,
    })

    assert hemorrhage.logic_rule(row) is True


def test_fail_no_data():
    row = {}

    assert hemorrhage.logic_rule(row) is False
