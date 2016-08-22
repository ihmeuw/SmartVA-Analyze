from smartva.rules import drowning_child as drowning
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.DROWNING: YES,
        VA.INJURY_DAYS: 0,
    }

    assert drowning.logic_rule(row) is True


def test_fail_drowning():
    row = {
        VA.DROWNING: NO,
    }

    assert drowning.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert drowning.logic_rule(row) is False
