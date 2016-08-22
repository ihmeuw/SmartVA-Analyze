# https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse/doc/md/measles.md
from smartva.data.constants import *
from smartva.utils.utils import value_from_row, int_or_float

CAUSE_ID = 10


def logic_rule(row):
    value_of = value_from_row(row, int_or_float)

    acute = value_of(Child.ILLNESS_DAYS) < 30

    face_rash = (value_of(Child.RASH) == YES
                 and (value_of(Child.RASH_LOCATION1) == Rash.FACE
                      or value_of(Child.RASH_LOCATION2) == Rash.FACE))

    measles_rash = value_of(Child.RASH_COLOR_WHITISH) == YES

    fever = value_of(Child.FEVER) == YES or value_of(Child.FREE_TEXT_FEVER) == YES

    cough = value_of(Child.COUGH) == YES

    diff_breathing = value_of(Child.BREATHING_DIFFICULT) == YES

    loose_stool = value_of(Child.LOOSE_STOOL) == YES or value_of(Child.FREE_TEXT_DIARRHEA) == YES

    pneumonia = value_of(Child.FREE_TEXT_PNEUMONIA) == YES

    return acute and (face_rash or measles_rash) and fever and (cough or diff_breathing) and (loose_stool or pneumonia)
