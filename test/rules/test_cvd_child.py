from smartva.rules import cvd_child as cvd
from smartva.data.constants import *

VA = Child


def test_pass():
    row = {
        VA.FREE_TEXT_HEART: YES,
    }

    assert cvd.logic_rule(row) is True


def test_fail():
    row = {
        VA.FREE_TEXT_HEART: NO,
    }

    assert cvd.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert cvd.logic_rule(row) is False
