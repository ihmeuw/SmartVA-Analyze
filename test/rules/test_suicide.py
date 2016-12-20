from smartva.rules import suicide
from smartva.data.constants import *


def test_adult_pass():
    row = {
        Adult.SELF_INFLICTED: YES,
        Adult.FREE_TEXT_SUICIDE: YES,
    }

    assert suicide.logic_rule(row) is True


def test_adult_pass_self_inflicted():
    row = {
        Adult.SELF_INFLICTED: YES,
    }

    assert suicide.logic_rule(row) is True


def test_adult_pass_free_text():
    row = {
        Adult.FREE_TEXT_SUICIDE: YES,
    }

    assert suicide.logic_rule(row) is True


def test_fail_no_data():
    row = {}

    assert suicide.logic_rule(row) is False
