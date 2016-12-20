from smartva.rules import poisoning_adult as poisoning
from smartva.data.constants import *

VA = Adult


def test_pass():
    row = {
        VA.POISONING: YES,
        VA.INJURY_DAYS: 0,
    }

    assert poisoning.logic_rule(row) is True


def test_fail_poisoning():
    row = {
        VA.POISONING: NO,
        VA.INJURY_DAYS: 0,
    }

    assert poisoning.logic_rule(row) is False


def test_fail_days():
    row = {
        VA.POISONING: YES,
        VA.INJURY_DAYS: 31,
    }

    assert poisoning.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert poisoning.logic_rule(row) is False
