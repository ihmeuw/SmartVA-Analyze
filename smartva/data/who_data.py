ADDITIONAL_HEADERS = [
    'sid',
    'gen_5_4',   # age unit
    'gen_5_4a',  # age in years
    'gen_5_4b',  # age in months
    'gen_5_4c',  # age in days
    'gen_5_4d',  # age group
    'agedays',
]

YES_NO_QUESTIONS = {
}


"""Recode categorical questions.

Schema
------
(PHMRC_COL, WHO_COL) {WHO_VALUE: PHMRC_VALUE}
"""
RECODE_QUESTIONS = {
}

RENAME_QUESTIONS = {
}

"""Create select one categoricals from a series of questions codes as yes/no.

Schema
------
PHMRC_COL: {PHMRC_VALUE: WHO_COL}
"""
REVERSE_ONE_HOT = {
}

"""Create multiselect questions from a series of questions codes as yes/no.

Schema
------
PHMRC_COL: {PHMRC_VALUE: WHO_COL}
"""
REVERSE_ONE_HOT_MULTISELECT = {
}

"""Change the values of multiselect questions.

Schema:
(PHMRC_COL, WHO_COL) : {WHO_VALUE: PHMRC_VALUE}
"""
RECODE_MULTISELECT = {
}


"""Create a yes/no columns from the value in a multiselect

Schema
------
PHMRC_COL: (WHO_COL, WHO_VALUE)
"""
ONE_HOT_FROM_MULTISELECT = {
}

"""Fill in unit columns based on the presence of a numeric value.

Schema
------
PHMRC_COL: (WHO_COL, UNIT)

The unit is the value the PHMRC_COL should take if the value in WHO_COL is
greater than one.
"""
UNIT_IF_AMOUNT = {
}


"""Convert durations variables where the units do not align across surveys.

Schema
------

(PHMRC_UNIT_COL, PHMRC_VALUE_COL, PHMRC_UNIT): {WHO_VALUE_COL: SCALAR}

The scalar is applied to the WHO value column to convert to the PHMRC unit
specific. The PHMRC unit column is filled if there is a non-zero value in any
of the WHO value columns.
"""
DURATION_CONVERSIONS = {
}

"""Convert a single duration column into a categorical.


Schema
------
(PHMRC_COL, WHO_COL): {(INTERVAL_START, INTERVAL_END): ENCODED_VALUE}

The PHMRC columns takes the value of encoded value if the duration in the WHO
column is within the interval.
"""
BIN_DURATIONS = {
}
