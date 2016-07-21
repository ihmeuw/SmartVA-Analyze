# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/hemorrhage.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 20


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    female = value_of(SEX) == FEMALE

    age = 12 < value_of(AGE) <= 49

    pregnant = value_of(Adult.PREGNANT) == YES

    period_overdue = value_of(Adult.PERIOD_OVERDUE) == YES and value_of(Adult.PERIOD_OVERDUE_DAYS) > 90

    delivering = value_of(Adult.DURING_ABORTION) == YES or value_of(Adult.DURING_CHILDBIRTH) == YES

    postpartum = value_of(Adult.AFTER_ABORTION) == YES or value_of(Adult.AFTER_CHILDBIRTH) == YES

    excessive_bleeding = (value_of(Adult.EXCESSIVE_VAGINAL_BLEEDING_1_WEEK) == YES
                          or value_of(Adult.EXCESSIVE_BLEEDING_DURING) == YES
                          or value_of(Adult.EXCESSIVE_BLEEDING_AFTER) == YES)

    return female and age and (pregnant or period_overdue or delivering or postpartum) and excessive_bleeding
