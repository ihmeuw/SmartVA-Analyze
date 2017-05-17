# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/rti.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 19


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    road_traffic = value_of(Child.ROAD_TRAFFIC) == YES

    recent = value_of(Child.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    return road_traffic and recent
