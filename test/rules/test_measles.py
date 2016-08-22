from smartva.rules import measles
from smartva.data.constants import *


def test_child_pass():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FEVER: YES,
        Child.COUGH: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is True


def test_child_pass_rash_whitish():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH_COLOR_WHITISH: YES,
        Child.FEVER: YES,
        Child.COUGH: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is True


def test_child_pass_fever_ft():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FREE_TEXT_FEVER: YES,
        Child.COUGH: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is True


def test_child_pass_diff_breathing():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FEVER: YES,
        Child.BREATHING_DIFFICULT: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is True


def test_child_pass_pneumonia():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FEVER: YES,
        Child.COUGH: YES,
        Child.FREE_TEXT_PNEUMONIA: YES,
    }

    assert measles.logic_rule(row) is True


def test_child_fail_acute():
    row = {
        Child.ILLNESS_DAYS: 30.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FEVER: YES,
        Child.COUGH: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is False


def test_child_fail_rash():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.FEVER: YES,
        Child.COUGH: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is False


def test_child_fail_fever():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.COUGH: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is False


def test_child_fail_cough():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FEVER: YES,
        Child.LOOSE_STOOL: YES,
    }

    assert measles.logic_rule(row) is False


def test_child_fail_loose_stool():
    row = {
        Child.ILLNESS_DAYS: 1.0,
        Child.RASH: YES,
        Child.RASH_LOCATION1: Rash.FACE,
        Child.FEVER: YES,
        Child.COUGH: YES,
    }

    assert measles.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert measles.logic_rule(row) is False
