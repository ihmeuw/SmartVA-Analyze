from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 13


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    heart = value_of(Child.FREE_TEXT_HEART) == YES

    return heart
