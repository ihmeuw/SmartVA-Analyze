MALE = 1
FEMALE = 2

NO = 0
YES = 1
REFUSED_TO_ANSWER = 8
UNKNOWN = 9

SEX = 'g5_02'
AGE = 'g5_04a'


class Adult(object):
    PALE = 'a2_20'
    BREATHING_DIFFICULT = 'a2_37'
    BREATHING_FAST = 'a2_40'
    CHEST_PAIN = 'a2_43'
    HEADACHES = 'a2_69'
    PERIOD_OVERDUE = 'a3_07'
    PERIOD_OVERDUE_DAYS = 'a3_08'
    PREGNANT = 'a3_10'
    AFTER_ABORTION = 'a3_17'
    AFTER_CHILDBIRTH = 'a3_18'
    FALL = 'a5_01_2'
    DROWNING = 'a5_01_3'
    BITE = 'a5_01_5'
    INJURY_DAYS = 'a5_04'


class Child(object):
    FALL = 'c4_47_2'
    DROWNING = 'c4_47_3'
    BITE = 'c4_47_5'
    INJURY_DAYS = 'c4_49'
    FREE_TEXT_CANCER = 'c_6_2'
