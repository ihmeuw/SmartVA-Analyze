import pytest
from smartva.rules import malnutrition
from smartva.data.constants import *


def test_child_pass():
    row = {
        Child.THIN_LIMBS: YES,
        Child.FLAKING_SKIN: YES,
        Child.HAIR_COLOR_CHANGE_RED_YELLOW: YES,
    }

    assert malnutrition.logic_rule(row) is True


@pytest.mark.xfail
def test_child_pass1():
    row = {
        Child.THIN_LIMBS: YES,
        Child.FLAKING_SKIN: YES,
        Child.PROTRUDING_BELLY: YES,
    }

    assert malnutrition.logic_rule(row) is True


def test_child_pass2():
    row = {
        Child.THIN_LIMBS: YES,
        Child.FLAKING_SKIN: YES,
        Child.LACK_OF_BLOOD: YES,
    }

    assert malnutrition.logic_rule(row) is True


def test_child_pass_kitchen_sink():
    row = {
        Child.THIN_LIMBS: YES,
        Child.FLAKING_SKIN: YES,
        Child.HAIR_COLOR_CHANGE_RED_YELLOW: YES,
        Child.PROTRUDING_BELLY: YES,
        Child.LACK_OF_BLOOD: YES,
    }

    assert malnutrition.logic_rule(row) is True


def test_fail_no_data():
    row = {}

    assert malnutrition.logic_rule(row) is False
