ADDITIONAL_HEADERS = [
    'sid',
    'gen_5_4',   # age unit
    'gen_5_4a',  # age in years
    'gen_5_4b',  # age in months
    'gen_5_4c',  # age in days
    'gen_5_4d',  # age group
    'agedays',

    'adult_5_2a',    # Injury, other specify
    'child_4_48a',   # Injury, other specify
    'adult_2_87a',   # Paralysis location, other specify
    'adult_4_2a',    # Tobacco kind, other specify
    'adult_2_83b',   # Convulsion value in hours
    'child_1_5b',
    'child_1_19a',   # stillbirth abnormalities, other specify
    'child_1_20a',   # no age when illness started in day
    'child_2_8a',    # birth water color, other specify
    'child_2_15a',   # birth attendant, other specify
    'child_3_3a',    # neonate abnormallities, other specify

    # Custom mappings
    'adult_2_44',
    'child_1_7',
    'child_1_25',
    'child_1_21',
    'child_1_21a',
    'child_1_21b',
    'child_1_21c',
    'child_1_25a',
    'child_1_25b',
    'child_1_25c',
    'child_1_26',
    'child_2_17',
    'child_3_8',
    'child_4_27',
]

YES_NO_QUESTIONS = {
    'adult_5_1': 'Id10077',
    'adult_5_3': 'Id10099',
    'adult_5_4': 'Id10100',
    'child_4_47': 'Id10077',
    'child_4_49': 'Id10100',

    'adult_1_1a': 'Id10135',
    'adult_1_1c': 'Id10137',
    'adult_1_1m': 'Id10138',
    'adult_1_1g': 'Id10134',
    'adult_1_1h': 'Id10136',
    'adult_1_1i': 'Id10133',
    'adult_1_1d': 'Id10125',
    'adult_1_1l': 'Id10141',
    'adult_1_1n': 'Id10127',

    'adult_2_2': 'Id10147',
    'adult_2_7': 'Id10233',
    'adult_2_10': 'Id10228',
    'adult_2_11': 'Id10229',
    'adult_2_13': 'Id10230',
    'adult_2_14': 'Id10231',
    'adult_2_21': 'Id10265',
    'adult_2_25': 'Id10247',
    'adult_2_27': 'Id10252',
    'adult_2_29': 'Id10255',
    'adult_2_30': 'Id10256',
    'adult_2_31': 'Id10257',
    'adult_2_32': 'Id10153',
    'adult_2_34': 'Id10155',
    'adult_2_35': 'Id10157',
    'adult_2_36': 'Id10159',
    'adult_2_43': 'Id10174',
    'adult_2_47': 'Id10181',
    'adult_2_50': 'Id10186',
    'adult_2_51': 'Id10187',
    'adult_2_52': 'Id10224',
    'adult_2_53': 'Id10189',
    'adult_2_55': 'Id10191',
    'adult_2_56': 'Id10192',
    'adult_2_57': 'Id10261',
    'adult_2_60': 'Id10264',
    'adult_2_61': 'Id10194',
    'adult_2_64': 'Id10200',
    'adult_2_67': 'Id10204',
    'adult_2_72': 'Id10208',
    'adult_2_74': 'Id10214',
    'adult_2_75': 'Id10217',
    'adult_2_77': 'Id10218',
    'adult_2_82': 'Id10219',
    'adult_2_84': 'Id10222',
    'adult_2_85': 'Id10258',

    'adult_3_1': 'Id10294',
    'adult_3_2': 'Id10295',
    'adult_3_3a': 'Id10296',
    'adult_3_3': 'Id10299',
    'adult_3_4': 'Id10300',
    'adult_3_5': 'Id10297',
    'adult_3_6': 'Id10301',
    'adult_3_7': 'Id10302',
    'adult_3_9': 'Id10304',
    'adult_3_10': 'Id10305',
    'adult_3_12': 'Id10335',
    'adult_3_13': 'Id10325',
    'adult_3_14': 'Id10328',
    'adult_3_15': 'Id10312',
    'adult_3_17': 'Id10336',
    'adult_3_18': 'Id10315',
    'adult_3_19': 'Id10329',

    'adult_4_1': 'Id10412',

    'adult_6_1': 'Id10432',
    'adult_6_3a': 'Id10435',
    'adult_6_4': 'Id10437',
    'adult_6_5': 'Id10438',

    'child_1_3': 'Id10356',
    'child_1_12': 'Id10104',
    'child_1_13': 'Id10109',
    'child_1_14': 'Id10110',
    'child_1_16': 'Id10115',
    'child_1_17': 'Id10116',
    'child_1_18': 'Id10370',

    'child_2_4': 'Id10377',

    'child_3_2': 'Id10370',
    'child_3_4': 'Id10111',
    'child_3_5': 'Id10112',
    'child_3_6': 'Id10113',
    'child_3_7': 'Id10105',
    'child_3_9': 'Id10107',
    'child_3_11': 'Id10271',
    'child_3_12': 'Id10272',
    'child_3_17': 'Id10159',
    'child_3_20': 'Id10166',
    'child_3_23': 'Id10172',
    'child_3_29': 'Id10284',
    'child_3_32': 'Id10286',
    'child_3_33': 'Id10281',
    'child_3_35': 'Id10287',
    'child_3_40': 'Id10240',
    'child_3_47': 'Id10289',
    'child_3_49': 'Id10290',

    'child_4_1': 'Id10147',
    'child_4_3': 'Id10149',
    'child_4_6': 'Id10181',
    'child_4_9': 'Id10185',
    'child_4_12': 'Id10153',
    'child_4_14': 'Id10156',
    'child_4_16': 'Id10159',
    'child_4_18': 'Id10166',
    'child_4_20': 'Id10172',
    'child_4_25': 'Id10220',
    'child_4_26': 'Id10214',
    'child_4_28': 'Id10208',
    'child_4_29': 'Id10278',
    'child_4_30': 'Id10233',
    'child_4_38': 'Id10238',
    'child_4_39': 'Id10267',
    'child_4_40': 'Id10200',
    'child_4_41': 'Id10268',
    'child_4_42': 'Id10256',
    'child_4_44': 'Id10241',
    'child_4_46': 'Id10239',

    'child_5_0a': 'Id10435',
    'child_5_1': 'Id10432',
    'child_5_4': 'Id10437',
    'child_5_5': 'Id10438',
    'child_5_10': 'Id10462',
    'child_5_17': 'Id10445',
    'child_5_19': 'Id10446',
}


"""Recode categorical questions.

Schema
------
(PHMRC_COL, WHO_COL) {WHO_VALUE: PHMRC_VALUE}
"""
RECODE_QUESTIONS = {
    ('gen_5_2', 'Id10019'): {'male': 1, 'female': 2, 'undetermined': 8},
    ('adult_2_4', 'Id10150'): {'mild': 1, 'moderate': 2, 'severe': 3,
                               'DK': 9, 'Ref': 8},
    ('adult_2_5', 'Id10151'): {'continuous': 1, 'on_and_off': 2, 'nightly': 3,
                               'DK': 9, 'Ref': 8},
    ('adult_2_9', 'Id10235'): {'face': 1, 'trunk': 2, 'extremities': 3,
                               'everywhere': 4, 'DK': 9, 'Ref': 8},
    ('adult_2_22', 'Id10266_units'): {'days': 4, 'months': 2, 'DK': 9, 'ref': 8},
    ('adult_2_26', 'Id10248_units'): {'days': 4, 'months': 2, 'DK': 9, 'ref': 8},
    ('adult_2_58', 'Id10262_units'): {'days': 4, 'months': 2, 'DK': 9, 'ref': 8},
    ('adult_2_62', 'id10196_unit'): {'hours': 5, 'days': 4, 'months': 2, 'DK': 9,
                                     'ref': 8},
    ('adult_2_65', 'Id10201_unit'): {'days': 4, 'months': 2, 'DK': 9, 'ref': 8},
    ('adult_2_59', 'Id10263'): {'solids': 1, 'liquids': 2, 'both': 3, 'DK': 9,
                                'Ref': 8},
    ('adult_2_63', 'Id10199'): {'upper_abdomen': 1, 'lower_abdomen': 2,
                                'upper_lower_abdomen': 9, 'DK': 9, 'Ref': 8},
    ('adult_2_66', 'Id10203'): {'rapidly': 1, 'slowly': 2, 'DK': 9, 'Ref': 8},
    ('adult_2_68', 'Id10205_unit'): {'days': 4, 'months': 2, 'DK': 9, 'ref': 8},
    ('adult_4_2', 'Id10414'): {
        'cigarettes': 1,
        'pipe': 2,
        'chewing_tobacco': 3,
        'local_form_of_tobacco': 4,
        'other': 11,
    },

    ('child_1_4', 'Id10357'): {'during_delivery': 1, 'after_delivery': 2,
                               'DK': 9, 'Ref': 8},
    ('child_1_6', 'Id10360'): {
        'hospital': 1,
        'other_health_facility': 2,
        'home': 4,
        'on_route_to_hospital_or_facility': 3,
        'other': 5,
        'DK': 9,
        'Ref': 8,
    },
    ('child_1_11', 'Id10114'): {'yes': 2, 'no': 1, 'dk': 9, 'ref': 8},
    ('child_2_8', 'Id10385'): {'green_or_brown': 1, 'clear': 2, 'other': 3,
                               'dk': 9, 'ref': 8},
    ('child_2_15', 'Id10339'): {
        'Doctor': 1,
        'Midwife': 2,
        'Nurse': 2,
        'Relative': 3,
        'Self_mother': 4,
        'Traditional_birth_attendant': 5,
        'Other': 6,
        'DK': 9,
        'ref': 8,
    },
    ('child_2_15', 'Id10339'): {
        'Doctor': 1,
        'Midwife': 2,
        'Nurse': 2,
        'Relative': 3,
        'Self_mother': 4,
        'Traditional_birth_attendant': 5,
        'Other': 6,
        'DK': 9,
        'ref': 8,
    },
    ('child_4_4', 'Id10150'): {'mild': 1, 'moderate': 2, 'severe': 3,
                               'DK': 9, 'Ref': 8},
}

RENAME_QUESTIONS = {
    'gen_6_7': 'Id10073',
    'gen_5_0': 'Id10017',
    'gen_5_0a': 'Id10018',
    'interviewdate': 'Id10012',
    'gen_2_3a': 'Id10057',

    'adult_2_22a': 'Id10266_a',
    'adult_2_22b': 'Id10266_b',
    'adult_2_26a': 'Id10248_a',
    'adult_2_26b': 'Id10248_b',
    'adult_2_58a': 'Id10262_a',
    'adult_2_58b': 'Id10262_b',
    'adult_2_62a': 'Id10196',
    'adult_2_62b': 'Id10197_a',
    'adult_2_62c': 'Id10198',
    'adult_2_65a': 'Id10201_a',
    'adult_2_65b': 'Id10202',
    'adult_2_68a': 'Id10205_a',
    'adult_2_68b': 'Id10206',
    'adult_2_83a': 'Id10221',
    'adult_3_8a': 'Id10303',
    'adult_3_11a': 'Id10309',
    'adult_3_16a': 'Id10332',
    'adult_4_4a': 'Id10415',
    'adult_6_3b': 'Id10436',
    'adult_6_8': 'Id10444',
    'adult_6_11': 'Id10464',
    'adult_6_12': 'Id10466',
    'adult_6_13': 'Id10468',
    'adult_6_14': 'Id10470',
    'adult_6_15': 'Id10472',
    'adult_7_c': 'Id10476',
    'child_1_8a': 'Id10366',
    'child_1_20a': 'Id10351',
    'child_1_20b': 'Id10352_a',
    'child_1_20c': 'Id10352_b',
    'child_2_10a': 'Id10382',
    'child_3_19a': 'Id10161_0',
    'child_3_22a': 'Id10167_a',
    'child_3_30a': 'Id10285',
    'child_4_7a': 'Id10183',
    'child_4_33a': 'Id10234',
    'child_5_0b': 'Id10436',
    'child_5_9': 'Id10444',
    'child_5_12': 'Id10464',
    'child_5_13': 'Id10466',
    'child_5_14': 'Id10468',
    'child_5_15': 'Id10470',
    'child_5_16': 'Id10472',
    'child_6_c': 'Id10476',
}

"""Create multiselect questions from a series of questions codes as yes/no.

Schema
------
PHMRC_COL: {PHMRC_VALUE: WHO_COL}
"""
REVERSE_ONE_HOT_MULTISELECT = {
    'adult_5_2': {
        'Id10079': 1,
        'Id10083': 2,
        'Id10085': 3,
        'Id10084': 4,
        'Id10086': 5,
        'Id10089': 6,
        'Id10090': 7,
        'Id10097': 11,
    },
    'child_4_48': {
        'Id10079': 1,
        'Id10083': 2,
        'Id10085': 3,
        'Id10084': 4,
        'Id10086': 5,
        'Id10089': 6,
        'Id10090': 7,
        'Id10097': 11,
    },
    'child_1_19': {
        'Id10373': 1,
        'Id10372': 2,
        'Id10371': 3,
    },
    'child_2_1': {
        'Id10399': 1,
        'Id10396': 2,
        'Id10401': 3,
        'Id10397': 4,
        'Id10403': 5,
        'Id10405': 6,
        'Id10404': 7,
        'Id10402': 8,
        'Id10395': 9,
    },
    'child_3_3': {
        'Id10373': 1,
        'Id10372': 2,
        'Id10371': 3,
    },
}

"""Change the values of multiselect questions.

Schema:
(PHMRC_COL, WHO_COL) : {WHO_VALUE: PHMRC_VALUE}
"""
RECODE_MULTISELECT = {
    ('adult_2_9', 'Id10235'): {
        'face': 1,
        'trunk': 2,
        'extremities': 3,
        'everywhere': 4,
        'DK': 9,
        'Ref': 8,
    },
    ('adult_2_87', 'Id10260'): {
        'right_side': 1,
        'left_side': 2,
        'lower_part_of_body': 3,
        'upper_part_of_body': 4,
        'one_leg_only': 5,
        'one_arm_only': 6,
        'whole_body': 7,
        'other': 11,
        'DK': 9,
        'Ref': 8,
    }
}


"""Create a yes/no columns from the value in a multiselect

Schema
------
PHMRC_COL: (WHO_COL, WHO_VALUE)
"""
ONE_HOT_FROM_MULTISELECT = {
    'child_4_23': ('Id10173_nc', 'grunting'),
    'adult_7_1': ('Id10477', 'Chronic_kidney_disease'),
    'adult_7_2': ('Id10477', 'Dialysis'),
    'adult_7_3': ('Id10477', 'Fever'),
    'adult_7_4': ('Id10477', 'Heart_attack'),
    'adult_7_5': ('Id10477', 'Heart_problem'),
    'adult_7_6': ('Id10477', 'Jaundice'),
    'adult_7_7': ('Id10477', 'Liver_failure'),
    'adult_7_8': ('Id10477', 'Malaria'),
    'adult_7_9': ('Id10477', 'Pneumonia'),
    'adult_7_10': ('Id10477', 'Renal_kidney_failure'),
    'adult_7_11': ('Id10477', 'Suicide'),
    'child_6_1': ('Id10478', 'abdomen'),
    'child_6_2': ('Id10478', 'cancer'),
    'child_6_3': ('Id10478', 'dehydration'),
    'child_6_4': ('Id10478', 'dengue'),
    'child_6_5': ('Id10478', 'diarrhea'),
    'child_6_6': ('Id10478', 'fever'),
    'child_6_7': ('Id10478', 'heart_problem'),
    'child_6_8': ('Id10478', 'jaundice'),
    'child_6_9': ('Id10478', 'pneumonia'),
    'child_6_10': ('Id10478', 'rash'),
    'neonate_6_1': ('Id10479', 'asphyxia'),
    'neonate_6_2': ('Id10479', 'incubator'),
    'neonate_6_3': ('Id10479', 'lung_problem'),
    'neonate_6_4': ('Id10479', 'pneumonia'),
    'neonate_6_5': ('Id10479', 'preterm_delivery'),
    'neonate_6_6': ('Id10479', 'respiratory_distress'),
}

"""Fill in unit columns based on the presence of a numeric value.

Schema
------
PHMRC_COL: (WHO_COL, UNIT)

The unit is the value the PHMRC_COL should take if the value in WHO_COL is
greater than one.
"""
UNIT_IF_AMOUNT = {
    'adult_2_83': ('Id10221', 6),
    'adult_3_8': ('Id10303', 3),
    'adult_3_11': ('Id10309', 2),
    'adult_3_16': ('Id10332', 5),
    'adult_4_4': ('Id10415', 1),
    'child_1_8': ('Id10366', 1),
    'child_1_20': {'Id10352_a': 2, 'Id10352_b': 1},
    'child_2_10': ('Id10382', 5),
    'child_3_19': ('Id10161_0', 4),
    'child_3_22': ('Id10167_a', 4),
    'child_3_30': ('Id10285', 4),
    'child_4_7': ('Id10183', 1),
    'child_4_33': ('Id10234', 4),
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
    ('adult_2_15', 'adult_2_15a', 4): {'Id10232_a': 1, 'Id10232_b': 30},
    ('child_1_5', 'child_1_5a', 4): {'Id10358': 30, 'Id10359': 1,
                                     'Id10359_a': 7},
    ('child_4_2', 'child_4_2a', 1): {'Id10148_b': 1, 'Id10148_c': 30},
    ('child_4_13', 'child_4_13a', 1): {'Id10154_a': 1, 'Id10154_b': 30},
}
