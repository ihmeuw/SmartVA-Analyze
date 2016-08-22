from smartva.rules import cancer_child as cancer
from smartva.data.constants import *


def test_pass():
    row = {
        Child.FREE_TEXT_CANCER: YES,
    }

    assert cancer.logic_rule(row) is True


def test_fail():
    row = {
        Child.FREE_TEXT_CANCER: NO,
    }

    assert cancer.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert cancer.logic_rule(row) is False
