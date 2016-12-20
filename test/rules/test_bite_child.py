from smartva.rules import bite_child as bite
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.BITE: YES,
        VA.INJURY_DAYS: 0,
    }

    assert bite.logic_rule(row) is True


def test_fail_bite():
    row = {
        VA.BITE: NO,
        VA.INJURY_DAYS: 0,
    }

    assert bite.logic_rule(row) is False


def test_fail_days():
    row = {
        VA.BITE: YES,
        VA.INJURY_DAYS: 31,
    }

    assert bite.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert bite.logic_rule(row) is False
