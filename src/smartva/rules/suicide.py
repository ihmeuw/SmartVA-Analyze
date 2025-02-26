# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/suicide.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 45


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    self_inflicted = value_of(Adult.SELF_INFLICTED) == YES

    free_text_suicide = value_of(Adult.FREE_TEXT_SUICIDE) == YES

    recent = value_of(Adult.INJURY_DAYS) < INJURY_DURATION_CUTTOFF

    no_injury = all([
        value_of(Adult.ROAD_TRAFFIC) != YES,
        value_of(Adult.FALL) != YES,
        value_of(Adult.DROWNING) != YES,
        value_of(Adult.POISONING) != YES,
        value_of(Adult.BITE) != YES,
        value_of(Adult.BURN) != YES,
        value_of(Adult.OTHER_INJURY) != YES,
        value_of(Adult.INFLICTED_BY_OTHER) != YES,   # exclude homicide also
    ])

    return (self_inflicted or free_text_suicide) and recent and no_injury
