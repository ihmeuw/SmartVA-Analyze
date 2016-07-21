# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/hypertensive.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 22


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    female = value_of(SEX) == FEMALE

    age = 12 < value_of(AGE) <= 49

    pregnant = value_of(Adult.PREGNANT) == YES

    period_overdue = value_of(Adult.PERIOD_OVERDUE) == YES and value_of(Adult.PERIOD_OVERDUE_DAYS) > 90

    convulsions = value_of(Adult.CONVULSIONS) == YES

    non_epileptic = value_of(Adult.EPILEPSY) == NO

    return female and age and (pregnant or period_overdue) and convulsions and non_epileptic
