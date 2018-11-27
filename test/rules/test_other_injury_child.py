from smartva.rules import other_injury_child as other_injury
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.OTHER_INJURY: YES,
        VA.INJURY_DAYS: 0,
    }

    assert other_injury.logic_rule(row) is True


def test_fail_other_injury():
    row = {
        VA.OTHER_INJURY: NO,
        VA.INJURY_DAYS: 0,
    }

    assert other_injury.logic_rule(row) is False


def test_fail_days():
    row = {
        VA.OTHER_INJURY: YES,
        VA.INJURY_DAYS: 31,
    }

    assert other_injury.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert other_injury.logic_rule(row) is False
