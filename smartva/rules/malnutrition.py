# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/pem.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 22


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    thin_limbs = value_of(Child.THIN_LIMBS) == YES

    flaking_skin = value_of(Child.FLAKING_SKIN) == YES

    hair_color = value_of(Child.HAIR_COLOR_CHANGE_RED_YELLOW) == YES

    protruding_belly = value_of(Child.PROTRUDING_BELLY) == YES

    pallor = value_of(Child.LACK_OF_BLOOD) == YES

    symptoms = thin_limbs + flaking_skin + hair_color + protruding_belly + pallor

    return symptoms >= 3
