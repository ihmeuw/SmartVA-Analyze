from smartva.data.common_data import ADULT

AGE_GROUP = ADULT
KEEP_PATTERN = r'(sid$|real|age$|sex$|cause$|restricted$|s\d+)'

GENERATED_VARS_DATA = {
    's88881': 0,
    's88882': 0,
    's88883': 0,
    's88884': 0,
    's36991': 0,
    's36992': 0,
    's18991': 0,
    's18992': 0,
    's19991': 0,
    's19992': 0,
    's23991': 0,
    's23992': 0,
    's23993': 0,
    's23994': 0,
    's56991': 0,
    's56992': 0,
    's56993': 0,
    's56994': 0,
    's55991': 0,
    's55992': 0,
    's64991': 0,
    's64992': 0,
    's82991': 0,
    's150991': 0,
    's150992': 0,
    'age': 0,
    'sex': 0,
    'restricted': '',
}

VAR_CONVERSION_MAP = {
    'sid': 'sid',
    'g5_02': 'real_gender',
    'g5_04a': 'real_age',
    'a1_01_1': 's1',
    'a1_01_2': 's2',
    'a1_01_3': 's3',
    'a1_01_4': 's4',
    'a1_01_5': 's5',
    'a1_01_6': 's6',
    'a1_01_7': 's7',
    'a1_01_8': 's8',
    'a1_01_9': 's9',
    'a1_01_10': 's10',
    'a1_01_11': 's11',
    'a1_01_12': 's12',
    'a1_01_13': 's13',
    'a1_01_14': 's14',
    'a2_01': 's15',
    'a2_02': 's16',
    'a2_03': 's17',
    'a2_04': 's18',
    'a2_05': 's19',
    'a2_06': 's20',
    'a2_07': 's21',
    'a2_08': 's22',
    'a2_09_1a': 's23',
    'a2_09_2a': 's25',
    'a2_10': 's27',
    'a2_11': 's28',
    'a2_12': 's29',
    'a2_13': 's30',
    'a2_14': 's31',
    'a2_15': 's32',
    'a2_16': 's33',
    'a2_17': 's34',
    'a2_18': 's35',
    'a2_19': 's36',
    'a2_20': 's37',
    'a2_21': 's38',
    'a2_22': 's39',
    'a2_23': 's40',
    'a2_24': 's41',
    'a2_25': 's42',
    'a2_26': 's43',
    'a2_27': 's44',
    'a2_28': 's45',
    'a2_29': 's46',
    'a2_30': 's47',
    'a2_31': 's48',
    'a2_32': 's49',
    'a2_33': 's50',
    'a2_34': 's51',
    'a2_35': 's52',
    'a2_36': 's53',
    'a2_37': 's54',
    'a2_38': 's55',
    'a2_39_1': 's56',
    'a2_39_2': 's57',
    'a2_40': 's58',
    'a2_41': 's59',
    'a2_42': 's60',
    'a2_43': 's61',
    'a2_44': 's62',
    'a2_45': 's63',
    'a2_46a': 's64',
    'a2_47': 's66',
    'a2_48': 's67',
    'a2_49': 's68',
    'a2_50': 's69',
    'a2_51': 's70',
    'a2_52': 's71',
    'a2_53': 's72',
    'a2_54': 's73',
    'a2_55': 's74',
    'a2_56': 's75',
    'a2_57': 's76',
    'a2_58': 's77',
    'a2_59': 's78',
    'a2_60': 's79',
    'a2_61': 's80',
    'a2_62': 's81',
    'a2_63_1': 's82',
    'a2_63_2': 's83',
    'a2_64': 's84',
    'a2_65': 's85',
    'a2_66': 's86',
    'a2_67': 's87',
    'a2_68': 's88',
    'a2_69': 's89',
    'a2_70': 's90',
    'a2_71': 's91',
    'a2_72': 's92',
    'a2_73': 's93',
    'a2_74': 's94',
    'a2_75': 's95',
    'a2_76': 's96',
    'a2_77': 's97',
    'a2_78': 's98',
    'a2_79': 's99',
    'a2_80': 's100',
    'a2_81': 's101',
    'a2_82': 's102',
    'a2_83': 's103',
    'a2_84': 's104',
    'a2_85': 's105',
    'a2_86': 's106',
    'a2_87_1': 's107',
    'a2_87_2': 's108',
    'a2_87_3': 's109',
    'a2_87_4': 's110',
    'a2_87_5': 's111',
    'a2_87_6': 's112',
    'a2_87_7': 's113',
    'a2_87_8': 's114',
    'a2_87_9': 's115',
    'a2_87_10a': 's116',
    'a3_01': 's118',
    'a3_02': 's119',
    'a3_03': 's120',
    'a3_04': 's121',
    'a3_05': 's122',
    'a3_06': 's123',
    'a3_07': 's124',
    'a3_08': 's125',
    'a3_09': 's126',
    'a3_10': 's127',
    'a3_11': 's128',
    'a3_12': 's129',
    'a3_13': 's130',
    'a3_14': 's131',
    'a3_15': 's132',
    'a3_16': 's133',
    'a3_17': 's134',
    'a3_18': 's135',
    'a3_19': 's136',
    'a3_20': 's137',
    'a4_01': 's138',
    'a4_02_1': 's139',
    'a4_02_2': 's140',
    'a4_02_3': 's141',
    'a4_02_4': 's142',
    'a4_02_5a': 's143',
    'a4_02_6': 's145',
    'a4_02_7': 's146',
    'a4_03': 's147',
    'a4_04': 's148',
    'a4_05': 's149',
    'a4_06': 's150',
    'a5_01_1': 's151',
    'a5_01_2': 's152',
    'a5_01_3': 's153',
    'a5_01_4': 's154',
    'a5_01_5': 's155',
    'a5_01_6': 's156',
    'a5_01_7': 's157',
    'a5_01_8': 's158',
    'a5_01_9a': 's159',
    'a5_02': 's161',
    'a5_03': 's162',
    'a5_04': 's163',
}

COPY_VARS = {
    'real_age': 'age',
    'real_gender': 'sex'
}

AGE_QUARTILE_BINARY_VARS = {
    'age': [
        (65, 's88884'),
        (49, 's88883'),
        (32, 's88882'),
        (0, 's88881')
    ]
}

DURATION_CUTOFF_DATA = {
    'age': 49,
    's15': 30,
    's17': 5,
    's22': 10,
    's32': 15,
    's39': 22.5,
    's41': 15,
    's43': 7,
    's45': 8,
    's50': 23.5,
    's54': 7,
    's59': 4,
    's67': 5,
    's73': 2,
    's77': 8,
    's81': 8,
    's85': 14,
    's88': 90,
    's90': .5416667,
    's93': 7,
    's96': .4166667,
    's99': 4,
    's103': .0208333,
    's106': 15,
    's125': 84,
    's128': 240,
    's133': .3541667,
    's147': 4,
    's148': 10
}

INJURY_VARS = {
    ('s163', 30): [
        's151',
        's152',
        's153',
        's154',
        's155',
        's156',
        's157',
        's159',
        's161',
        's162'
    ]
}

BINARY_CONVERSION_MAP = {
    's36': {
        1: 's36991',
        2: 's36992',
        3: 's36992',
    },
    's18': {
        1: 's18991',
        2: 's18992',
        3: 's18992',
    },
    's19': {
        1: 's19991',
        2: 's19992',
    },
    's23': {
        1: 's23991',
        2: 's23992',
        3: 's23993',
        4: 's23994',
    },
    # This is correct...
    's25': {
        1: 's23991',
        2: 's23992',
        3: 's23993',
        4: 's23994',
    },
    's56': {
        1: 's56991',
        2: 's56992',
        3: 's56993',
        4: 's56994',
    },
    's55': {
        1: 's55991',
        2: 's55992',
    },
    's64': {
        1: 's64991',
        2: 's64991',
        3: 's64992',
    },
    's82': {
        2: 's82991',
    },
    's150': {
        1: 's150991',
        2: 's150992',
        3: 's150992',
    },
    's62': [3],
    's78': [3],
    's86': [2],
    's91': [1],
    's95': [1],
    's100': [1],
    's107': [1],
    's108': {
        1: 's107'
    },
    'sex': [2]
}

BINARY_VARS = [
    's1',
    's2',
    's3',
    's4',
    's5',
    's6',
    's7',
    's8',
    's9',
    's10',
    's11',
    's12',
    's13',
    's14',
    's16',
    's20',
    's21',
    's27',
    's28',
    's29',
    's30',
    's31',
    's33',
    's34',
    's35',
    's37',
    's38',
    's40',
    's42',
    's44',
    's46',
    's47',
    's48',
    's49',
    's51',
    's52',
    's53',
    's58',
    's60',
    's61',
    's63',
    's66',
    's68',
    's69',
    's70',
    's71',
    's72',
    's74',
    's75',
    's76',
    's79',
    's80',
    's84',
    's87',
    's89',
    's92',
    's94',
    's97',
    's98',
    's101',
    's102',
    's104',
    's105',
    's107',
    's109',
    's110',
    's111',
    's112',
    's113',
    's114',
    's115',
    's116',
    's118',
    's119',
    's120',
    's121',
    's122',
    's123',
    's124',
    's126',
    's127',
    's129',
    's130',
    's131',
    's132',
    's134',
    's135',
    's136',
    's137',
    's138',
    's139',
    's140',
    's141',
    's142',
    's143',
    's145',
    's146',
    's149',
    's151',
    's152',
    's153',
    's154',
    's155',
    's156',
    's157',
    's158',
    's159',
    's161',
    's162'
]

DROP_LIST = [
    's163',
    's36',
    's18',
    's19',
    's23',
    's25',
    's56',
    's55',
    's64',
    's82',
    's150',
    's108'
]

CENSORED_MAP = {
    4: [   # Asthma
        's109',      # Paralyzed lower part of body
        's110',      # Paralyzed upper part of body
        's111',      # Paralyzed one leg only
        's112',      # Paralyzed one arm only
        's114',      # Paralyzed refused
        's115',      # Paralyzed don't know
        's116',      # Paralyzed other
        's119',      # Did [name] have any ulcers (pits) in the breast?
        's122',      # Did [name] have vaginal bleeding other than her period? (intermenstrual)
        's123',      # Was there excessive vaginal bleeding in the week prior to death?
        's125',      # For how many weeks was her period overdue? [days]
        's126',      # Did [name] have a sharp pain in the belly shortly before death?
        's127',      # Was [name] pregnant at the time of death?
        's128',      # For how many months was she pregnant? [days]
        's129',      # Did [name] die during an abortion?
        's130',      # Did bleeding occur while she was pregnant?
        's131',      # Did she have excessive bleeding during labor or delivery?
        's132',      # Did she die during labor or delivery?
        's133',      # For how long was she in labor? [days]
        's134',      # Did she die within 6 weeks after having an abortion?
        's135',      # Did she die within 6 weeks of childbirth?
        's136',      # Did she have excessive bleeding after delivery or abortion?
        's140',      # Type of tobacco used: pipe
        's143',      # Type of tobacco used: other
        's145',      # Type of tobacco used: refused
        's151',      # Decedent suffered road traffic injury
        's153',      # Decedent suffered drowning
        's154',      # Decedent suffered poisoning
        's155',      # Decedent suffered bite/sting
        's156',      # Decedent suffered burn
        's157',      # Decedent victim of violence
        's159',      # Decedent suffered other injury
        's161',      # Was the injury or accident self-inflicted?
        's162',      # Was the injury or accident intentionally inflicted by someone else?
        's23991',    # Rash was located on face
        's23993',    # Rash was located on extremities
        's23994',    # Rash was located everywhere
        's30',       # Did [name] have an ulcer (pit) on the foot?
        's31',       # Did the ulcer ooze pus?
        's32',       # For how many days did the ulcer ooze pus? [days]
        's47',       # Did [name] have a lump in the armpit?
        's48',       # Did [name] have a lump in the groin?
        's8',        # Did Decedent Have Epilepsy?
        's81',       # For how long before death did [name] have belly pain? [days]
        's85',       # For how long before death did [name] have a protruding belly? [days]
        's88',       # For how long before death did [name] have a mass in the belly [days]
        's92',       # Did [name] have a stiff neck?
        's93',       # For how long before death did [name] have stiff neck? [days]
        's9999104',  # word_liver
        's9999148',  # word_suicid
        's999999',   # word_kidney
        's3',        # Did Decedent Have Cancer?
        's12',       # Did Decedent Have Stroke?
        's13',       # Did Decedent Have TB?
        's39',       # For how long did [name] have the yellow discoloration? [days]
        's52',       # Did [name] cough blood?
        's107',      # Paralyzed on one side (arm and leg)
    ],
    11: [   # Diabetes with Coma
        's12',       # Did Decedent Have Stroke?
        's107',      # Paralyzed on one side (arm and leg)
        's109',      # Paralyzed lower part of body
        's110',      # Paralyzed upper part of body
        's111',      # Paralyzed one leg only
        's112',      # Paralyzed one arm only
        's114',      # Paralyzed refused
        's115',      # Paralyzed don't know
        's116',      # Paralyzed other
    ],
    12: [   # Diabetes with Renal Failure
        's12',       # Did Decedent Have Stroke?
        's107',      # Paralyzed on one side (arm and leg)
        's109',      # Paralyzed lower part of body
        's110',      # Paralyzed upper part of body
        's111',      # Paralyzed one leg only
        's112',      # Paralyzed one arm only
        's114',      # Paralyzed refused
        's115',      # Paralyzed don't know
        's116',      # Paralyzed other
    ],
    13: [   # Diabetes with Skin Infection/Sepsis
        's12',       # Did Decedent Have Stroke?
        's107',      # Paralyzed on one side (arm and leg)
        's109',      # Paralyzed lower part of body
        's110',      # Paralyzed upper part of body
        's111',      # Paralyzed one leg only
        's112',      # Paralyzed one arm only
        's114',      # Paralyzed refused
        's115',      # Paralyzed don't know
        's116',      # Paralyzed other
    ],
    14: [   # Diarrhea/Dysentery
        's61',        # Did [name] experience pain in the chest in the month preceding death?
        's1',         # Did Decedent Have Asthma?
        's12',        # Did Decedent Have Stroke?
        's42',        # Did [name] have puffiness of the face?
        's97',        # Did it continue until death?
        's86',        # Slowly protruding belly
    ],
    16: [   # Epilepsy
        's23992',     # Rash was located on trunk
        's23993',     # Rash was located on extremities
        's31',        # Did the ulcer ooze pus?
        's32',        # For how many days did the ulcer ooze pus? [days]
        's62',        # Pain greater than 24 hours
        's70',        # Was there blood in the stool up until death?
        's74',        # Was there blood in the vomit?
        's88',        # For how long before death did [name] have a mass in the belly [days]
        's93',        # For how long before death did [name] have stiff neck? [days]
        's107',       # Paralyzed on one side (arm and leg)
        's110',       # Paralyzed upper part of body
        's111',       # Paralyzed one leg only
        's115',       # Paralyzed don't know
        's119',       # Did [name] have any ulcers (pits) in the breast?
        's124',       # At the time of death was her period overdue?
        's125',       # For how many weeks was her period overdue? [days]
        's126',       # Did [name] have a sharp pain in the belly shortly before death?
        's128',       # For how many months was she pregnant? [days]
        's130',       # Did bleeding occur while she was pregnant?
        's131',       # Did she have excessive bleeding during labor or delivery?
        's132',       # Did she die during labor or delivery?
        's133',       # For how long was she in labor? [days]
        's134',       # Did she die within 6 weeks after having an abortion?
        's135',       # Did she die within 6 weeks of childbirth?
        's136',       # Did she have excessive bleeding after delivery or abortion?
        's154',       # Decedent suffered poisoning
        's159',       # Decedent suffered other injury
        's161',       # Was the injury or accident self-inflicted?
        's155',       # Decedent suffered bite/sting
        's156',       # Decedent suffered burn
        's157',       # Decedent victim of violence
        's162',       # Was the injury or accident intentionally inflicted by someone else?
        's999952',    # word_dialysi
        's999997',    # word_jaundic
        's999999',    # word_kidney
        's9999104',   # word_liver
        's9999108',   # word_malaria
        's9999130',   # word_renal
        's9999148',   # word_suicid
        's13',        # Did Decedent Have TB?
        's3',         # Did Decedent Have Cancer?
        's31',        # Did the ulcer ooze pus?
        's32',        # For how many days did the ulcer ooze pus? [days]
        's62',        # Pain greater than 24 hours
        's69',        # Was there blood in the stool?
        's70',        # Was there blood in the stool up until death?
        's70',        # Was there blood in the stool up until death?
        's9999108',   # word_malaria
        's9999130',   # word_renal
        's999997',    # word_jaundic

    ],
}

REQUIRED_MAP = {
    14: [   # Diarrhea/Dysentery
        's66',        # Did [name] have more frequent loose or liquid stools than usual?
    ],
    17: [   # Esophageal Cancer
        's76',         # Did [name] have difficulty swallowing?
    ]
}
