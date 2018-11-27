from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 1


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    hiv_positive = value_of(Child.HIV_POSITIVE_TEST) == YES

    return hiv_positive
