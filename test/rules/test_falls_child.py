from smartva.rules import falls_child as falls
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.FALL: YES,
        VA.INJURY_DAYS: 0,
    }

    assert falls.logic_rule(row) is True


def test_fail_falls():
    row = {
        VA.FALL: NO,
        VA.INJURY_DAYS: 0,
    }

    assert falls.logic_rule(row) is False


def test_fail_days():
    row = {
        VA.FALL: YES,
        VA.INJURY_DAYS: 31,
    }

    assert falls.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert falls.logic_rule(row) is False
