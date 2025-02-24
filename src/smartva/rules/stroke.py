from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 44


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    stroke = value_of(Adult.STROKE) == YES
    paralysis_one_side = (value_of(Adult.PARALYSIS_RIGHT) == YES or
                          value_of(Adult.PARALYSIS_LEFT) == YES)

    any_paralysis_or_stroke = any([
        stroke,
        paralysis_one_side,
        value_of(Adult.PARALYSIS_LOWER) == YES,
        value_of(Adult.PARALYSIS_UPPER) == YES,
        value_of(Adult.PARALYSIS_ONE_LEG) == YES,
        value_of(Adult.PARALYSIS_ONE_ARM) == YES,
        value_of(Adult.PARALYSIS_WHOLE) == YES,
        value_of(Adult.PARALYSIS_OTHER) == YES,
    ])

    diabetes = value_of(Adult.DIABETES) == YES

    pneumonia = value_of(Adult.FREE_TEXT_PNEUMONIA) == YES

    return ((stroke and paralysis_one_side) or
            (diabetes and any_paralysis_or_stroke) or
            (pneumonia and any_paralysis_or_stroke))
