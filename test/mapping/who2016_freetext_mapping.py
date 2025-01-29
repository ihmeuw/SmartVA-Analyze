from itertools import product

ADULT_WORD_COLUMNS = [
    #'adult_5_2a',  # no equivalent in WHO2016
    'Id10436',  # adult_6_3b
    'Id10444',  # adult_6_8
    'Id10464',  # adult_6_11
    'Id10466',  # adult_6_12
    'Id10468',  # adult_6_13
    'Id10470',  # adult_6_14
    'Id10472',  # adult_6_15
    'Id10476',  #adult_7_c  (only on PHMRC long questionnaire)
]

ADULT_WORD_SYMPTOMS = {
    's99991': [
        'abdomen',
    ],
    's99992': [
        'accid',
    ],
    's99993': [
        'alcohol',
    ],
    's99994': [
        'ami',
    ],
    's99995': [
        'amput',
    ],
    's99996': [
        'anemia',
    ],
    's99997': [
        'antibiot',
    ],
    's99998': [
        'appetit',
    ],
    's99999': [
        'arrest',
    ],
    's999910': [
        'arteri',
    ],
    's999911': [
        'asthma',
    ],
    's999912': [
        'attack',
    ],
    's999913': [
        'babi',
    ],
    's999914': [
        'bacteria',
    ],
    's999915': [
        'biopsi',
    ],
    's999916': [
        'birth',
    ],
    's999917': [
        'bite',
    ],
    's999918': [
        'black',
    ],
    's999919': [
        'blood',
        'bleed',
        'the bleeding in the'
    ],
    's999920': [
        'bone',
    ],
    's999921': [
        'born',
    ],
    's999922': [
        'bowel',
    ],
    's999923': [
        'brain',
    ],
    's999924': [
        'breast',
    ],
    's999925': [
        'breath',
    ],
    's999926': [
        'broken',
    ],
    's999927': [
        'cancer',
    ],
    's999928': [
        'cardio',
    ],
    's999929': [
        'cardiomegali',
    ],
    's999930': [
        'cathet',
    ],
    's999931': [
        'cerebr',
    ],
    's999932': [
        'cervix',
    ],
    's999933': [
        'cesarean',
    ],
    's999934': [
        'chemotherapi',
    ],
    's999935': [
        'chest',
    ],
    's999936': [
        'chronic',
    ],
    's999937': [
        'cirrhosi',
    ],
    's999938': [
        'clot',
    ],
    's999939': [
        'collapse',   # words ending in 's' are stemmed
    ],
    's999940': [
        'colon',
    ],
    's999941': [
        'coma',
    ],
    's999942': [
        'congest',
    ],
    's999943': [
        'conscious',
    ],
    's999944': [
        'convulse',   # words ending in 's' are stemmed
    ],
    's999945': [
        'copd',
    ],
    's999946': [
        'cough',
    ],
    's999947': [
        'ctscan',
    ],
    's999948': [
        'cut',
    ],
    's999949': [
        'deliv',
    ],
    's999950': [
        'depress',
    ],
    's999951': [
        'diabet',
    ],
    's999952': [
        'dialysi',
    ],
    's999953': [
        'diarrhea',
    ],
    's999954': [
        'digest',
    ],
    's999955': [
        'dizzi',
    ],
    's999956': [
        'drink',
    ],
    's999957': [
        'drown',
    ],
    's999958': [
        'dyspnea',
    ],
    's999959': [
        'ecg',
    ],
    's999960': [
        'edema',
    ],
    's999961': [
        'electr',
    ],
    's999962': [
        'encephalopathi',
    ],
    's999963': [
        'enlarg',
    ],
    's999964': [
        'epilepsi',
    ],
    's999965': [
        'esophag',
    ],
    's999966': [
        'failur',
    ],
    's999967': [
        'faint',
    ],
    's999968': [
        'fall',
    ],
    's999969': [
        'fever',
    ],
    's999970': [
        'finger',
    ],
    's999971': [
        'fire',
    ],
    's999972': [
        'fluid',
    ],
    's999973': [
        'foot',
    ],
    's999974': [
        'fractur',
    ],
    's999975': [
        'goiter',
    ],
    's999976': [
        'hand',
    ],
    's999977': [
        'head',
    ],
    's999978': [
        'headach',
    ],
    's999979': [
        'heart',
    ],
    's999980': [
        'hematoma',
    ],
    's999981': [
        'hemorrhag',
    ],
    's999982': [
        'hepat',
    ],
    's999983': [
        'hernia',
    ],
    's999984': [
        'hiv',
    ],
    's999985': [
        'hypertense',   # words ending in 's' are stemmed
    ],
    's999986': [
        'hypovolem',
    ],
    's999987': [
        'icu',
    ],
    's999988': [
        'infarct',
    ],
    's999989': [
        'infect',
    ],
    's999990': [
        'inflam',
    ],
    's999991': [
        'inhal',
    ],
    's999992': [
        'injuri',
    ],
    's999993': [
        'intestin',
    ],
    's999994': [
        'intracerebr',
    ],
    's999995': [
        'intub',
    ],
    's999996': [
        'ischemia',
    ],
    's999997': [
        'jaundic',
    ],
    's999998': [
        'kerosen',
    ],
    's999999': [
        'kidney',
    ],
    's9999100': [
        'kill',
    ],
    's9999101': [
        'knee',
    ],
    's9999102': [
        'labor',
    ],
    's9999103': [
        'leukemia',
    ],
    's9999104': [
        'liver',
    ],
    's9999105': [
        'lump',
    ],
    's9999106': [
        'lung',
    ],
    's9999107': [
        'lymphoma',
    ],
    's9999108': [
        'malaria',
    ],
    's9999109': [
        'mass',
    ],
    's9999110': [
        'mellitus',
    ],
    's9999111': [
        'mental',
    ],
    's9999112': [
        'motorcycl',
    ],
    's9999113': [
        'neck',
    ],
    's9999114': [
        'nephropathi',
    ],
    's9999115': [
        'nerv',
    ],
    's9999116': [
        'numb',
    ],
    's9999117': [
        'obstruct',
    ],
    's9999118': [
        'organ',
    ],
    's9999119': [
        'pain',
    ],
    's9999120': [
        'paralyz',
    ],
    's9999121': [
        'phlegm',
    ],
    's9999122': [
        'pneumonia',
    ],
    's9999123': [
        'poison',
    ],
    's9999124': [
        'polic',
    ],
    's9999125': [
        'pregnanc',
    ],
    's9999126': [
        'prostat',
    ],
    's9999127': [
        'puffi',
    ],
    's9999128': [
        'pulmonari',
    ],
    's9999129': [
        'pus',
    ],
    's9999130': [
        'renal',
    ],
    's9999131': [
        'respiratori',
    ],
    's9999132': [
        'ruptur',
    ],
    's9999133': [
        'seizur',
    ],
    's9999134': [
        'sepsi',
    ],
    's9999135': [
        'sever',
    ],
    's9999136': [
        'shock',
    ],
    's9999137': [
        'shot',
    ],
    's9999138': [
        'skin',
    ],
    's9999139': [
        'smoke',
    ],
    's9999140': [
        'snake',
    ],
    's9999141': [
        'stomach',
    ],
    's9999142': [
        'stomachach',
    ],
    's9999143': [
        'stone',
    ],
    's9999144': [
        'stool',
    ],
    's9999145': [
        'stress',
    ],
    's9999146': [
        'stroke',
    ],
    's9999147': [
        'sugar',
    ],
    's9999148': [
        'suicid',
    ],
    's9999149': [
        'surgeri',
    ],
    's9999150': [
        'suspect',
    ],
    's9999151': [
        'swell',
    ],
    's9999152': [
        'tetanus',
    ],
    's9999153': [
        'throat',
    ],
    's9999154': [
        'tongu',
    ],
    's9999155': [
        'transfus',
    ],
    's9999156': [
        'tree',
    ],
    's9999157': [
        'tumor',
    ],
    's9999158': [
        'ulcer',
    ],
    's9999159': [
        'ultrasound',
    ],
    's9999160': [
        'unconsci',
    ],
    's9999161': [
        'urin',
    ],
    's9999162': [
        'uterus',
    ],
    's9999163': [
        'vascular',
    ],
    's9999164': [
        'vehicular',
    ],
    's9999165': [
        'virus',
    ],
    's9999166': [
        'vomit',
    ],
    's9999167': [
        'water',
    ],
    's9999168': [
        'womb',
    ],
    's9999169': [
        'wound',
    ],
    's9999170': [
        'xray',
    ],
    's9999171': [
        'yellow',
    ],
}

CHILD_WORD_COLUMNS = [
    #'child_1_19a',  # no equivalent in WHO2016
    'Id10436',  # child_5_0b
    'Id10444',  # child_5_9
    'Id10464',  # child_5_12
    'Id10466',  # child_5_13
    'Id10468',  # child_5_14
    'Id10470',  # child_5_15
    'Id10472',  # child_5_16
    'Id10476',  # child_6_c  (only on PHMRC long questionnaire)
]

CHILD_WORD_SYMPTOMS = {
    's99991': [
        'abdomen',
    ],
    's99992': [
        'accid',
    ],
    's99993': [
        'asthma',
    ],
    's99994': [
        'bite',
    ],
    's99995': [
        'blood',
    ],
    's99996': [
        'bluish',
    ],
    's99997': [
        'brain',
    ],
    's99998': [
        'breath',
    ],
    's99999': [
        'cancer',
    ],
    's999910': [
        'chest',
    ],
    's999911': [
        'cold',
    ],
    's999912': [
        'convulse',   # words ending in 's' are stemmed
    ],
    's999913': [
        'cough',
    ],
    's999914': [
        'dehydr',
    ],
    's999915': [
        'dengu',
    ],
    's999916': [
        'diarrhea',
    ],
    's999917': [
        'drown',
    ],
    's999918': [
        'fall',
    ],
    's999919': [
        'fever',
    ],
    's999920': [
        'fire',
    ],
    's999921': [
        'glucose',   # words ending in 's' are stemmed
    ],
    's999922': [
        'head',
    ],
    's999923': [
        'heart',
    ],
    's999924': [
        'icu',
    ],
    's999925': [
        'injuri',
    ],
    's999926': [
        'jaundic',
    ],
    's999927': [
        'kidney',
    ],
    's999928': [
        'leukemia',
    ],
    's999929': [
        'lung',
    ],
    's999930': [
        'malaria',
    ],
    's999931': [
        'malnutrit',
    ],
    's999932': [
        'neck',
    ],
    's999933': [
        'pneumonia',
    ],
    's999934': [
        'poison',
    ],
    's999935': [
        'pox',
    ],
    's999936': [
        'pulmonari',
    ],
    's999937': [
        'rash',
    ],
    's999938': [
        'respiratori',
    ],
    's999939': [
        'road',
    ],
    's999940': [
        'scan',
    ],
    's999941': [
        'sepsi',
    ],
    's999942': [
        'shock',
    ],
    's999943': [
        'skin',
    ],
    's999944': [
        'snake',
    ],
    's999945': [
        'stomach',
    ],
    's999946': [
        'stool',
    ],
    's999947': [
        'swell',
    ],
    's999948': [
        'vomit',
    ],
    's999949': [
        'yellow',
    ],
}

NEONATE_WORD_COLUMNS = [
    #'child_1_19a',  # no equivalent in WHO2016
    #'child_3_3a',   # no equivalent in WHO2016
    'Id10436',  # child_5_0b
    'Id10444',  # child_5_9
    'Id10464',  # child_5_12
    'Id10466',  # child_5_13
    'Id10468',  # child_5_14
    'Id10470',  # child_5_15
    'Id10472',  # child_5_16
    'Id10476',  # child_6_c  (only on PHMRC long questionnaire)
]

NEONATE_WORD_SYMPTOMS = {
    's99991': [
        'abdomen',
    ],
    's99992': [
        'anemia',
    ],
    's99993': [
        'asphyxia',
    ],
    's99994': [
        'blood',
    ],
    's99995': [
        'breech',
    ],
    's99996': [
        'bwt',
    ],
    's99997': [
        'cesarean',
    ],
    's99998': [
        'color',
    ],
    's99999': [
        'cord',
    ],
    's999910': [
        'cri',
    ],
    's999911': [
        'distress',
    ],
    's999912': [
        'fetal',
    ],
    's999913': [
        'head',
    ],
    's999914': [
        'heart',
    ],
    's999915': [
        'heartbeat',
    ],
    's999916': [
        'hemorrhag',
    ],
    's999917': [
        'hypertensive',    # words ending in 's' are stemmed
    ],
    's999918': [
        'incub',
    ],
    's999919': [
        'induc',
    ],
    's999920': [
        'infect',
    ],
    's999921': [
        'labor',
    ],
    's999922': [
        'live',
    ],
    's999923': [
        'lung',
    ],
    's999924': [
        'movement',
    ],
    's999925': [
        'neonatorum',
    ],
    's999926': [
        'oxygen',
    ],
    's999927': [
        'pneumonia',
    ],
    's999928': [
        'pneumothorax',
    ],
    's999929': [
        'prenat',
    ],
    's999930': [
        'preterm',
    ],
    's999931': [
        'respiratori',
    ],
    's999932': [
        'sepsi',
    ],
    's999933': [
        'stillbirth',
    ],
    's999934': [
        'swell',
    ],
    's999935': [
        'twin',
    ],
    's999936': [
        'ventil',
    ],
    's999937': [
        'weight',
    ],
}

MODULE_ENCODING = {'adult': 3, 'child': 2, 'neonate': 1}
MAPPING_DATA = {
    'adult': (ADULT_WORD_COLUMNS, ADULT_WORD_SYMPTOMS),
    'child': (CHILD_WORD_COLUMNS, CHILD_WORD_SYMPTOMS),
    'neonate': (NEONATE_WORD_COLUMNS, NEONATE_WORD_SYMPTOMS),
}
MAPPING = []
for module, (columns, word_symptoms) in list(MAPPING_DATA.items()):
    for col, (symp, texts) in product(columns, list(word_symptoms.items())):
        for text in texts:
            MAPPING.append({
                'sid': 'Free text "{}" in "{}"'.format(text, col),
                'symptom': symp,
                col: text,
                'module': module,
                'endorsed': True,
            })
