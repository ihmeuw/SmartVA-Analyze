from smartva.rules import homicide_child as homicide
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.NO_INJURY: NO,
        VA.INFLICTED_BY_OTHER: YES,
    }

    assert homicide.logic_rule(row) is True


def test_fail_no_injury():
    row = {
        VA.NO_INJURY: YES,
    }

    assert homicide.logic_rule(row) is False


def test_fail_not_inflicted():
    row = {
        VA.NO_INJURY: NO,
        VA.INFLICTED_BY_OTHER: NO,
    }

    assert homicide.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert homicide.logic_rule(row) is False
