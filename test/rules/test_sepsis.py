from smartva.rules import sepsis
from smartva.data.constants import *

BASE_ROW = {
    SEX: FEMALE,
    AGE: 12.0,
    Adult.PERIOD_OVERDUE: NO,
    Adult.PERIOD_OVERDUE_DAYS: 0.0,
    Adult.PREGNANT: NO,
    Adult.AFTER_ABORTION: NO,
    Adult.AFTER_CHILDBIRTH: NO,
    Adult.BELLY_PAIN: NO,
    Adult.BELLY_PAIN_LOCATION1: UNKNOWN,
    Adult.BELLY_PAIN_LOCATION2: UNKNOWN,
    Adult.FEVER: NO,
    Adult.OFFENSIVE_VAGINAL_DISCHARGE: NO,
}


def test_logic_pass():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is True


def test_logic_fail_age_min():
    row = BASE_ROW.copy()
    row.update({
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is False


def test_logic_fail_age_max():
    row = BASE_ROW.copy()
    row.update({
        AGE: 50.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is False


def test_logic_fail_gender():
    row = BASE_ROW.copy()
    row.update({
        SEX: MALE,
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is False


def test_logic_pass_period():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PERIOD_OVERDUE: YES,
        Adult.PERIOD_OVERDUE_DAYS: 91.0,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is True


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

    assert sepsis.logic_rule(row) is False


def test_logic_pass_after_abortion():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
        Adult.AFTER_ABORTION: YES,
    })

    assert sepsis.logic_rule(row) is True


def test_logic_pass_after_childbirth():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
        Adult.AFTER_CHILDBIRTH: YES,
    })

    assert sepsis.logic_rule(row) is True


def test_logic_pass_pain_location1():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.BELLY_PAIN_LOCATION2: BellyPain.UPPER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is True


def test_logic_pass_pain_location2():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.UPPER_BELLY,
        Adult.BELLY_PAIN_LOCATION2: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is True


def test_logic_fail_pain():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: NO,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is False


def test_logic_fail_fever():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: NO,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: YES,
    })

    assert sepsis.logic_rule(row) is False


def test_logic_fail_discharge():
    row = BASE_ROW.copy()
    row.update({
        AGE: 13.0,
        Adult.PREGNANT: YES,
        Adult.FEVER: YES,
        Adult.BELLY_PAIN: YES,
        Adult.BELLY_PAIN_LOCATION1: BellyPain.LOWER_BELLY,
        Adult.OFFENSIVE_VAGINAL_DISCHARGE: NO,
    })

    assert sepsis.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert sepsis.logic_rule(row) is False
