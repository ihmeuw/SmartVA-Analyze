# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/oth_preg.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 36


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)
    
    female = value_of(SEX) == FEMALE

    age = MATERNAL_AGE_LOWER < value_of(AGE) <= MATERNAL_AGE_UPPER

    delivering = value_of(Adult.DURING_CHILDBIRTH) == YES

    long_delivery = value_of(Adult.LABOR_DURATION) >= PROLONGED_DELIVERY_CUTTOFF

    return female and age and delivering and long_delivery
