# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/hypertensive.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 22


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    female = value_of(SEX) == FEMALE

    age = MATERNAL_AGE_LOWER < value_of(AGE) <= MATERNAL_AGE_UPPER

    pregnant = value_of(Adult.PREGNANT) == YES

    period_overdue = value_of(Adult.PERIOD_OVERDUE) == YES and value_of(Adult.PERIOD_OVERDUE_DAYS) > PERIOD_OVERDUE_CUTTOFF

    convulsions = value_of(Adult.CONVULSIONS) == YES and  value_of(Adult.EPILEPSY) == YES

    return female and age and (pregnant or period_overdue) and convulsions
