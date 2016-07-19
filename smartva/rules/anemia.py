# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/anemia.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 3


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    female = value_of(SEX) == FEMALE

    age = 12 < value_of(AGE) <= 49

    pregnant = value_of(Adult.PREGNANT) == YES

    period_overdue = value_of(Adult.PERIOD_OVERDUE) == YES and value_of(Adult.PERIOD_OVERDUE_DAYS) > 90

    postpartum = value_of(Adult.AFTER_ABORTION) == YES or value_of(Adult.AFTER_CHILDBIRTH) == YES

    # Symptoms
    pale = value_of(Adult.PALE) == YES

    breathing = value_of(Adult.BREATHING_DIFFICULT) == YES or value_of(Adult.BREATHING_FAST) == YES

    chest_pain = value_of(Adult.CHEST_PAIN) == YES

    headaches = value_of(Adult.HEADACHES) == YES

    symptoms = pale + breathing + chest_pain + headaches

    return female and age and (pregnant or period_overdue or postpartum) and symptoms >= 3
