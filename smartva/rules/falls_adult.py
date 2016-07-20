# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/falls.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 18


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    return value_of(Adult.FALL) == YES and value_of(Adult.INJURY_DAYS) < 30
