# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/fires.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 19


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    burn = value_of(Adult.BURN) == YES

    recent = value_of(Adult.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    return burn and recent
