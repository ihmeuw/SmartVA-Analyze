# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/suicide.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 45


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    self_inflicted = value_of(Adult.SELF_INFLICTED) == YES

    free_text_suicide = value_of(Adult.FREE_TEXT_SUICIDE) == YES

    return self_inflicted or free_text_suicide
