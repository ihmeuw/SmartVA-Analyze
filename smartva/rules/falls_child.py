# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/falls.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 6


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    fall = value_of(Child.FALL) == YES

    recent = value_of(Child.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    return fall and recent
