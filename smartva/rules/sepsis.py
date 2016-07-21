# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/sepsis.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 42


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    female = value_of(SEX) == FEMALE

    age = 12 < value_of(AGE) <= 49

    pregnant = value_of(Adult.PREGNANT) == YES

    period_overdue = value_of(Adult.PERIOD_OVERDUE) and value_of(Adult.PERIOD_OVERDUE_DAYS) > 90

    postpartum = value_of(Adult.AFTER_ABORTION) == YES or value_of(Adult.AFTER_CHILDBIRTH) == YES

    belly_pain = value_of(Adult.BELLY_PAIN) == YES

    in_lower_belly = (value_of(Adult.BELLY_PAIN_LOCATION1) == BellyPain.LOWER_BELLY
                      or value_of(Adult.BELLY_PAIN_LOCATION2) == BellyPain.LOWER_BELLY)

    fever = value_of(Adult.FEVER) == YES

    discharge = value_of(Adult.OFFENSIVE_VAGINAL_DISCHARGE) == YES

    return (female and age and (pregnant or period_overdue or postpartum)
            and fever and belly_pain and in_lower_belly and discharge)
