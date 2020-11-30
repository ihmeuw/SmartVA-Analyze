# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/homicide.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 21  # Violent death


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    injury_by_other = any([
        value_of(Child.INFLICTED_BY_OTHER) == YES,
        value_of(Child.VIOLENCE) == YES,
    ])
    recent = value_of(Child.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    no_unintentional_injury = all([
        value_of(Child.ROAD_TRAFFIC) != YES,
        value_of(Child.FALL) != YES,
        value_of(Child.DROWNING) != YES,
        value_of(Child.POISONING) != YES,
        value_of(Child.BITE) != YES,
        value_of(Child.BURN) != YES,
        value_of(Child.OTHER_INJURY) != YES,
    ])

    return injury_by_other and recent and no_unintentional_injury
