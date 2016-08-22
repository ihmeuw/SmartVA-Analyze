# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/homicide.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 21


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    return value_of(Adult.NO_INJURY) != YES and value_of(Adult.INFLICTED_BY_OTHER) == YES
