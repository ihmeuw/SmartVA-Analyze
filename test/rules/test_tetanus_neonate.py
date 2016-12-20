import pytest
from smartva.rules import tetanus_neonate
from smartva.data.constants import *


def test_neonate_pass():
    row = {
        Neonate.CONVULSIONS: YES,
        Neonate.UNRESPONSIVE: YES,
        Neonate.OPEN_MOUTH: NO,
        Neonate.NORMAL_SUCKLING: YES,
        Neonate.STOPPED_NORMAL_SUCKLING: YES,
    }

    assert tetanus_neonate.logic_rule(row) is True


def test_neonate_fail_convulsions():
    row = {
        Neonate.CONVULSIONS: NO,
        Neonate.UNRESPONSIVE: YES,
        Neonate.OPEN_MOUTH: NO,
        Neonate.NORMAL_SUCKLING: YES,
        Neonate.STOPPED_NORMAL_SUCKLING: YES,
    }

    assert tetanus_neonate.logic_rule(row) is False


@pytest.mark.xfail
def test_neonate_fail_unresponsive():
    row = {
        Neonate.CONVULSIONS: YES,
        Neonate.UNRESPONSIVE: NO,
        Neonate.OPEN_MOUTH: NO,
        Neonate.NORMAL_SUCKLING: YES,
        Neonate.STOPPED_NORMAL_SUCKLING: YES,
    }

    assert tetanus_neonate.logic_rule(row) is False


@pytest.mark.xfail
def test_neonate_fail_open_mouth():
    row = {
        Neonate.CONVULSIONS: YES,
        Neonate.UNRESPONSIVE: YES,
        Neonate.OPEN_MOUTH: YES,
        Neonate.NORMAL_SUCKLING: YES,
        Neonate.STOPPED_NORMAL_SUCKLING: YES,
    }

    assert tetanus_neonate.logic_rule(row) is False


def test_neonate_fail_normal_suckling():
    row = {
        Neonate.CONVULSIONS: YES,
        Neonate.UNRESPONSIVE: YES,
        Neonate.OPEN_MOUTH: NO,
        Neonate.NORMAL_SUCKLING: NO,
        Neonate.STOPPED_NORMAL_SUCKLING: YES,
    }

    assert tetanus_neonate.logic_rule(row) is False


def test_neonate_fail_stop_suckling():
    row = {
        Neonate.CONVULSIONS: YES,
        Neonate.UNRESPONSIVE: YES,
        Neonate.OPEN_MOUTH: NO,
        Neonate.NORMAL_SUCKLING: YES,
        Neonate.STOPPED_NORMAL_SUCKLING: NO,
    }

    assert tetanus_neonate.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert tetanus_neonate.logic_rule(row) is False
