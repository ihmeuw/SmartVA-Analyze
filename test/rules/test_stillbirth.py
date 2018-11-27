from smartva.rules import stillbirth
from smartva.data.constants import *


def test_neonate_pass():
    row = {
        Neonate.NEVER_CRIED_MOVED_BREATHED: YES,
    }

    assert stillbirth.logic_rule(row) is True


def test_neonate_fail():
    row = {
        Neonate.NEVER_CRIED_MOVED_BREATHED: NO,
    }

    assert stillbirth.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert stillbirth.logic_rule(row) is False
