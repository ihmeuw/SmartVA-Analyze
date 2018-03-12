CHECKLIST_WORD_SYMPTOMS = {
    'adult': {
        'adult_7_1': 's999999',
        'adult_7_2': 's999952',
        'adult_7_3': 's999969',
        'adult_7_4': 's99994',
        'adult_7_5': 's999979',
        'adult_7_6': 's999997',
        'adult_7_7': 's9999104',
        'adult_7_8': 's9999108',
        'adult_7_9': 's9999122',
        'adult_7_10': 's9999130',
        'adult_7_11': 's9999148',
    },
    'child': {
        'child_6_1': 's99991',
        'child_6_2': 's99999',
        'child_6_3': 's999914',
        'child_6_4': 's999915',
        'child_6_5': 's999916',
        'child_6_6': 's999919',
        'child_6_7': 's999923',
        'child_6_8': 's999926',
        'child_6_9': 's999933',
        'child_6_10': 's999937',
    },
    'neonate': {
        'neonate_6_1': 's99993',
        'neonate_6_2': 's999918',
        'neonate_6_3': 's999923',
        'neonate_6_4': 's999927',
        'neonate_6_5': 's999930',
        'neonate_6_6': 's999911',
    },
}

MODULE_ENCODING = {'adult': 3, 'child': 2, 'neonate': 1}
VALUES = {1: True, 0: False, '': False, 'X': False}
MAPPING = []

for module, mapping_data in CHECKLIST_WORD_SYMPTOMS.items():
    for col, symp in mapping_data.items():
        for value, endorsed in VALUES.items():
            MAPPING.append({
                'sid': '"{}" with value "{}"'.format(col, value),
                'symptom': symp,
                col: value,
                'gen_3_1': 1,
                'gen_5_4d': MODULE_ENCODING[module],
                'module': module,
                'endorsed': endorsed,
            })