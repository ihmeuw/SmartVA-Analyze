# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/falls.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 18


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    fall = value_of(Adult.FALL) == YES

    recent = value_of(Adult.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    unintentional = value_of(Adult.SELF_INFLICTED) != YES and value_of(Adult.INFLICTED_BY_OTHER) != YES

    return fall and recent and unintentional
