# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/bite.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 5


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    bite = value_of(Adult.BITE) == YES

    recent = value_of(Adult.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    return bite and recent
