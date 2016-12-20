from smartva.rules import fires_child as fires
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.BURN: YES,
        VA.INJURY_DAYS: 0,
    }

    assert fires.logic_rule(row) is True


def test_fail_fires():
    row = {
        VA.BURN: NO,
        VA.INJURY_DAYS: 0,
    }

    assert fires.logic_rule(row) is False


def test_fail_days():
    row = {
        VA.BURN: YES,
        VA.INJURY_DAYS: 31,
    }

    assert fires.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert fires.logic_rule(row) is False
