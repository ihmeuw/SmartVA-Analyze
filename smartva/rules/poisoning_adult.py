# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/poisoning.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 38


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    poisoning = value_of(Adult.POISONING) == YES

    terminal = value_of(Adult.INJURY_DAYS) < 30

    return poisoning and terminal
