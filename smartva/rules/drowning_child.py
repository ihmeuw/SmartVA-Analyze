# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/drowning.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 4


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    drowning = value_of(Child.DROWNING) == YES

    recent = value_of(Child.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    unintentional = value_of(Child.INFLICTED_BY_OTHER) != YES

    return drowning and recent and unintentional
