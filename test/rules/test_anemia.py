from smartva.rules import anemia
from smartva.data.constants import *

BASE_ROW = {
    SEX: FEMALE,
    AGE: 12.0,
    Adult.PERIOD_OVERDUE: NO,
    Adult.PERIOD_OVERDUE_DAYS: 0.0,
    Adult.PREGNANT: NO,
    Adult.AFTER_ABORTION: NO,
    Adult.AFTER_CHILDBIRTH: NO,
    Adult.PALE: NO,
    Adult.BREATHING_DIFFICULT: NO,
    Adult.BREATHING_FAST: NO,
    Adult.CHEST_PAIN: NO,
    Adult.HEADACHES: NO,
}


def test_logic_fail_age_min():
    row = BASE_ROW.copy()
    row.update({
        Adult.PREGNANT: YES,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_age_max():
    row = BASE_ROW.copy()
    row.update({
        AGE: 50,
        Adult.PREGNANT: YES,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is False


def test_logic_fail_gender():
    row = BASE_ROW.copy()
    row.update({
        SEX: MALE,
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is False



def test_logic_pass_period():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PERIOD_OVERDUE: YES,
        Adult.PERIOD_OVERDUE_DAYS: 91.0,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is True


def test_logic_fail_period():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PERIOD_OVERDUE: YES,
        Adult.PERIOD_OVERDUE_DAYS: 90.0,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is False


def test_logic_pass_postpartum2():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.AFTER_CHILDBIRTH: YES,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is True


def test_logic_pass_symptoms1():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.PALE: YES,
        Adult.BREATHING_DIFFICULT: YES,
    })

    assert anemia.logic_rule(row) is True


def test_fail_no_data():
    row = {}

    assert anemia.logic_rule(row) is False
