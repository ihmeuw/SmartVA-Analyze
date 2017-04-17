from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 23


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    diabetes = value_of(ADULT.DIABETES) == YES
    heart_disease = value_of(ADULT.HEART_DISEASE) == YES
    free_text_heart = (value_of(ADULT.FREE_TEXT_HEART_ATTACK) == YES or
                       value_of(ADULT.FREE_TEXT_HEART_PROBLEM) == YES)

    return diabetes and (heart_disease or free_text_heart)
