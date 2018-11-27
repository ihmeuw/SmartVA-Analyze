from smartva.rules import road_traffic_adult as road_traffic
from smartva.data.constants import *

VA = Adult


def test_pass():
    row = {
        VA.ROAD_TRAFFIC: YES,
        VA.INJURY_DAYS: 0,
    }

    assert road_traffic.logic_rule(row) is True


def test_fail_road_traffic():
    row = {
        VA.ROAD_TRAFFIC: NO,
        VA.INJURY_DAYS: 0,
    }

    assert road_traffic.logic_rule(row) is False


def test_fail_days():
    row = {
        VA.ROAD_TRAFFIC: YES,
        VA.INJURY_DAYS: 31,
    }

    assert road_traffic.logic_rule(row) is False


def test_fail_no_data():
    row = {}

    assert road_traffic.logic_rule(row) is False
