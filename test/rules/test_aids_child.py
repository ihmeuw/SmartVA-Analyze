from smartva.rules import aids_child as aids
from smartva.data.constants import *

VA = Child


def test_pass_both():
    row = {
        VA.HIV_POSITIVE_TEST: YES,
        VA.HIV_POSITIVE_PROFESSIONAL: YES,
    }

    assert aids.logic_rule(row) is True


def test_pass_positive_test():
    row = {
        VA.HIV_POSITIVE_TEST: YES,
        VA.HIV_POSITIVE_PROFESSIONAL: NO,
    }

    assert aids.logic_rule(row) is True


def test_pass_positive_professional():
    row = {
        VA.HIV_POSITIVE_TEST: NO,
        VA.HIV_POSITIVE_PROFESSIONAL: YES,
    }

    assert aids.logic_rule(row) is True

def test_fail_neither():
    row = {
        VA.HIV_POSITIVE_TEST: NO,
        VA.HIV_POSITIVE_PROFESSIONAL: NO,
    }

    assert aids.logic_rule(row) is False
