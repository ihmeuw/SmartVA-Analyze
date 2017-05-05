from smartva.rules import stroke
from smartva.data.constants import *

VA = Adult


def test_pass():
    row = {
        VA.STROKE: YES,
        VA.PARALYSIS_RIGHT: YES,
    }

    assert stroke.logic_rule(row) is True


def test_fail_no_data():
    row = {}

    assert stroke.logic_rule(row) is False
