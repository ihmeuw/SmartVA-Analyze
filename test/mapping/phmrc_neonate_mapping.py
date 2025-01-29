MAPPING = [
    {
        'sid': 'Multiple birth (single)',
        'symptom': 's5',
        'child_1_1': 1,
        'endorsed': False,
    },
    {
        'sid': 'Multiple birth (double)',
        'symptom': 's5',
        'child_1_1': 2,
        'endorsed': True,
    },
    {
        'sid': 'Multiple birth (missing)',
        'symptom': 's5',
        'child_1_1': 9,
        'endorsed': False,
    },
    {
        'sid': 'Not first born (first)',
        'symptom': 's6',
        'child_1_2': 1,
        'endorsed': False,
    },
    {
        'sid': 'Not first born (second)',
        'symptom': 's6',
        'child_1_2': 2,
        'endorsed': True,
    },
    {
        'sid': 'Not first born (third or more)',
        'symptom': 's6',
        'child_1_2': 3,
        'endorsed': True,
    },
    {
        'sid': 'Not first born (missing)',
        'symptom': 's6',
        'child_1_2': 9,
        'endorsed': False,
    },
    {
        'sid': 'Mother alive',
        'symptom': 's7',
        'child_1_3': 1
    },
    {
        'sid': 'Mother died during delivery (during)',
        'symptom': 's8991',
        'child_1_4': 1,
        'endorsed': True,
    },
    {
        'sid': 'Mother died during delivery (after)',
        'symptom': 's8991',
        'child_1_4': 2,
        'endorsed': False,
    },
    {
        'sid': 'Mother died during delivery (missing)',
        'symptom': 's8991',
        'child_1_4': 9,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery (during)',
        'symptom': 's8992',
        'child_1_4': 1,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery (after)',
        'symptom': 's8992',
        'child_1_4': 2,
        'endorsed': True,
    },
    {
        'sid': 'Mother died after delivery (missing)',
        'symptom': 's8992',
        'child_1_4': 9,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (missing)',
        'symptom': 's9',
        'child_1_5': 9,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (days-yes)',
        'symptom': 's9',
        'child_1_5': 4,
        'child_1_5a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Mother died after delivery duration (days-no)',
        'symptom': 's9',
        'child_1_5': 4,
        'child_1_5a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (days-threshold)',
        'symptom': 's9',
        'child_1_5': 4,
        'child_1_5a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Mother died after delivery duration (days-no-empty)',
        'symptom': 's9',
        'child_1_5': 4,
        'child_1_5a': '',
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (days-invalid)',
        'symptom': 's9',
        'child_1_5': 4,
        'child_1_5a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (days-no-no unit)',
        'symptom': 's9',
        'child_1_5': '',
        'child_1_5a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (months-yes)',
        'symptom': 's9',
        'child_1_5': 2,
        'child_1_5b': 1,
        'endorsed': True,
    },
    {
        'sid': 'Mother died after delivery duration (months-no)',
        'symptom': 's9',
        'child_1_5': 2,
        'child_1_5b': 0,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (months-no-empty)',
        'symptom': 's9',
        'child_1_5': 2,
        'child_1_5b': '',
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (months-no-invalid)',
        'symptom': 's9',
        'child_1_5': 2,
        'child_1_5b': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (months-no-no unit)',
        'symptom': 's9',
        'child_1_5': '',
        'child_1_5b': 1,
        'endorsed': False,
    },
    {
        'sid': 'Mother died after delivery duration (float)',
        'symptom': 's9',
        'child_1_5': 4,
        'child_1_5a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    # It appears that s10 never existed
    {
        'sid': 'Born not in a health facility (hospital)',
        'symptom': 's11991',
        'child_1_6': 1,
        'endorsed': False,
    },
    {
        'sid': 'Born not in a health facility (other health facility)',
        'symptom': 's11991',
        'child_1_6': 2,
        'endorsed': False,
    },
    {
        'sid': 'Born not in a health facility (on route to facility)',
        'symptom': 's11991',
        'child_1_6': 3,
        'endorsed': False,
    },
    {
        'sid': 'Born not in a health facility (home)',
        'symptom': 's11991',
        'child_1_6': 4,
        'endorsed': True,
    },
    {
        'sid': 'Born not in a health facility (other)',
        'symptom': 's11991',
        'child_1_6': 5,
        'endorsed': True,
    },
    {
        'sid': 'Born not in a health facility (missing)',
        'symptom': 's11991',
        'child_1_6': 9,
        'endorsed': False,
    },
    {
        'sid': 'Birth size-small (very small)',
        'symptom': 's13',
        'child_1_7': 1,
        'endorsed': True,
    },
    {
        'sid': 'Birth size-small (small)',
        'symptom': 's13',
        'child_1_7': 2,
        'endorsed': True,
    },
    {
        'sid': 'Birth size-small (average)',
        'symptom': 's13',
        'child_1_7': 3,
        'endorsed': False,
    },
    {
        'sid': 'Birth size-small (large)',
        'symptom': 's13',
        'child_1_7': 4,
        'endorsed': False,
    },
    {
        'sid': 'Birth size-small (missing)',
        'symptom': 's13',
        'child_1_7': 9,
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (missing)',
        'symptom': 's14',
        'child_1_8': 9,
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (grams-yes)',
        'symptom': 's14',
        'child_1_8': 1,
        'child_1_8a': 2777,
        'endorsed': True,
    },
    {
        'sid': 'Birth weight (grams-no)',
        'symptom': 's14',
        'child_1_8': 1,
        'child_1_8a': 2000,
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (grams-no-invalid)',
        'symptom': 's14',
        'child_1_8': 1,
        'child_1_8a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (grams-no-no unit)',
        'symptom': 's14',
        'child_1_8': '',
        'child_1_8a': 2777,
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (grams-threshold)',
        'symptom': 's14',
        'child_1_8': 1,
        'child_1_8a': 2500,
        'endorsed': True,
    },
    {
        'sid': 'Birth weight (grams-float)',
        'symptom': 's14',
        'child_1_8': 1,
        'child_1_8a': 2725.2,
        'endorsed': True,  # floats are legal for weight values
    },
    {
        'sid': 'Birth weight (grams-no value)',
        'symptom': 's14',
        'child_1_8': 1,
        'child_1_8a': '',
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (kilograms-yes)',
        'symptom': 's14',
        'child_1_8': 2,
        'child_1_8b': 3,
        'endorsed': True,
    },
    {
        'sid': 'Birth weight (kilograms-no)',
        'symptom': 's14',
        'child_1_8': 2,
        'child_1_8b': 2,
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (kilograms-threshold)',
        'symptom': 's14',
        'child_1_8': 2,
        'child_1_8b': 2.5,
        'endorsed': True,
    },
    {
        'sid': 'Birth weight (kilograms-float)',
        'symptom': 's14',
        'child_1_8': 2,
        'child_1_8b': 2.7,
        'endorsed': True,  # floats are legal for weight values
    },
    {
        'sid': 'Birth weight (kilograms-no value)',
        'symptom': 's14',
        'child_1_8': 2,
        'child_1_8b': '',
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (kilograms-invalid)',
        'symptom': 's14',
        'child_1_8': 2,
        'child_1_8b': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (kilograms-no unit)',
        'symptom': 's14',
        'child_1_8': '',
        'child_1_8b': 2,
        'endorsed': False,
    },
    {
        'sid': 'Birth weight (missing)',
        'symptom': 's14',
        'child_1_8': 9,
        'endorsed': False,
    },
    # s15 was sex==male, but was dropped because it duplicates 'sex'
    {
        'sid': 'Born dead (alive)',
        'symptom': 's16',
        'child_1_11': 1,
        'endorsed': False,
    },
    {
        'sid': 'Born dead (dead)',
        'symptom': 's16',
        'child_1_11': 2,
        'endorsed': True,
    },
    {
        'sid': 'Born dead (missing)',
        'symptom': 's16',
        'child_1_11': 9,
        'endorsed': False,
    },
    {
        'sid': 'Baby cried',
        'symptom': 's17',
        'child_1_12': 1
    },
    {
        'sid': 'Baby moved',
        'symptom': 's18',
        'child_1_13': 1
    },
    {
        'sid': 'Baby breathed',
        'symptom': 's19',
        'child_1_14': 1
    },
    # Stillbirth abnormalities were dropped from the analysis. These were
    # initially used to distinguish different types of stillbirth
    # These include s20 to s27
    {
        'sid': 'Age illness started (missing)',
        'symptom': 's28',
        'child_1_20': 9,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (days-yes)',
        'symptom': 's28',
        'child_1_20': 4,
        'child_1_20a': 4,
        'endorsed': True,
    },
    {
        'sid': 'Age illness started (days-no)',
        'symptom': 's28',
        'child_1_20': 4,
        'child_1_20a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (days-no-empty)',
        'symptom': 's28',
        'child_1_20': 4,
        'child_1_20a': '',
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (days-no-invalid)',
        'symptom': 's28',
        'child_1_20': 4,
        'child_1_20a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (days-no-no unit)',
        'symptom': 's28',
        'child_1_20': '',
        'child_1_20a': 4,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (days-threshold)',
        'symptom': 's28',
        'child_1_20': 4,
        'child_1_20a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Age illness started (months-yes)',
        'symptom': 's28',
        'child_1_20': 2,
        'child_1_20b': 1,
        'endorsed': True,
    },
    {
        'sid': 'Age illness started (months-no)',
        'symptom': 's28',
        'child_1_20': 2,
        'child_1_20b': 0,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (months-no-empty)',
        'symptom': 's28',
        'child_1_20': 2,
        'child_1_20b': '',
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (months-no-invalid)',
        'symptom': 's28',
        'child_1_20': 2,
        'child_1_20b': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (months-no-no unit)',
        'symptom': 's28',
        'child_1_20': '',
        'child_1_20b': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (years-yes)',
        'symptom': 's28',
        'child_1_20': 1,
        'child_1_20c': 1,
        'endorsed': True,
    },
    {
        'sid': 'Age illness started (years-no)',
        'symptom': 's28',
        'child_1_20': 1,
        'child_1_20c': 0,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (years-no-empty)',
        'symptom': 's28',
        'child_1_20': 1,
        'child_1_20c': '',
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (years-no-invalid)',
        'symptom': 's28',
        'child_1_20': 1,
        'child_1_20c': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (years-no-no unit)',
        'symptom': 's28',
        'child_1_20': '',
        'child_1_20c': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age illness started (float)',
        'symptom': 's28',
        'child_1_20': 4,
        'child_1_20a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Illness duration (missing)',
        'symptom': 's29',
        'child_1_21': 9,
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (days-yes)',
        'symptom': 's29',
        'child_1_21': 4,
        'child_1_21a': 10,
        'endorsed': True,
    },
    {
        'sid': 'Illness duration (days-no)',
        'symptom': 's29',
        'child_1_21': 4,
        'child_1_21a': 2,
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (days-no-empty)',
        'symptom': 's29',
        'child_1_21': 4,
        'child_1_21a': '',
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (days-no-invalid)',
        'symptom': 's29',
        'child_1_21': 4,
        'child_1_21a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (days-no-no unit)',
        'symptom': 's29',
        'child_1_21': '',
        'child_1_21a': 10,
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (days-threshold)',
        'symptom': 's29',
        'child_1_21': 4,
        'child_1_21a': 3,
        'endorsed': True,
    },
    {
        'sid': 'Illness duration (months-yes)',
        'symptom': 's29',
        'child_1_21': 2,
        'child_1_21b': 1,
        'endorsed': True,
    },
    {
        'sid': 'Illness duration (months-no)',
        'symptom': 's29',
        'child_1_21': 2,
        'child_1_21b': 0,
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (months-no-empty)',
        'symptom': 's29',
        'child_1_21': 2,
        'child_1_21b': '',
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (months-no-invalid)',
        'symptom': 's29',
        'child_1_21': 2,
        'child_1_21b': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (months-no-no unit)',
        'symptom': 's29',
        'child_1_21': '',
        'child_1_21b': 1,
        'endorsed': False,
    },
    {
        'sid': 'Illness duration (float)',
        'symptom': 's29',
        'child_1_21': 4,
        'child_1_21a': 15.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Didn\'t die in a health facility (hospital)',
        'symptom': 's30991',
        'child_1_22': 1,
        'endorsed': False,
    },
    {
        'sid': 'Didn\'t die in a health facility (other health facility)',
        'symptom': 's30991',
        'child_1_22': 2,
        'endorsed': False,
    },
    {
        'sid': 'Didn\'t die in a health facility (on route to facility)',
        'symptom': 's30991',
        'child_1_22': 3,
        'endorsed': True,
    },
    {
        'sid': 'Didn\'t die in a health facility (home)',
        'symptom': 's30991',
        'child_1_22': 4,
        'endorsed': True,
    },
    {
        'sid': 'Didn\'t die in a health facility (other)',
        'symptom': 's30991',
        'child_1_22': 5,
        'endorsed': True,
    },
    {
        'sid': 'Didn\'t die in a health facility (missing)',
        'symptom': 's30991',
        'child_1_22': 9,
        'endorsed': False,
    },
    # Age symptoms were previously derived from corresponding questions from
    # child_1_25. Currently this are derived from the `agedays` from ODK. We
    # ignore the age calculated from the gen_5_4 columns
    {
        'sid': 'Child age at death (missing)',
        'symptom': 's31',
        'agedays': '',
        'endorsed': False,
    },
    {
        'sid': 'Child age at death (days-yes)',
        'symptom': 's31',
        'agedays': 5,
        'endorsed': True,
    },
    {
        'sid': 'Child age at death (days-no)',
        'symptom': 's31',
        'agedays': 2,
        'endorsed': False,
    },
    {
        # The threshold should be 10 months. However, ODK uses 28 days per month
        # in the `agedays` calculation. If the respondent says 10 months, this
        # symptom is not endorsed.
        'sid': 'Child age at death (days-threshold)',
        'symptom': 's31',
        'agedays': 3,
        'endorsed': True,
    },
    {
        'sid': 'Neonate module indicator',
        'symptom': 's32',
        'agedays': 7,
        'endorsed': True,
    },
    {
        'sid': 'Neonate module indicator (upper threshold)',
        'symptom': 's32',
        'agedays': 28,
        'endorsed': True,
    },
    {
        'sid': 'Neonate module indicator (lower threshold)',
        'symptom': 's32',
        'agedays': 1,
        'endorsed': True,
    },
    {
        'sid': 'Neonate module indicator (missing)',
        'symptom': 's32',
        'agedays': '',
        'endorsed': False,   # FIXME: Default is age 0
    },
    {
        'sid': 'Neonate module indicator (age zero)',
        'symptom': 's32',
        'agedays': 0,
        'endorsed': False,   # FIXME: age zero is still neonate
    },
    {
        'sid': 'Maternal convulsions during pregnancy',
        'symptom': 's33',
        'child_2_1': '1',
        'endorsed': True,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (multiple)',
        'symptom': 's33',
        'child_2_1': '3 1 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (duplicate)',
        'symptom': 's33',
        'child_2_1': '3 1 1 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (ignore constraint)',
        'symptom': 's33',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 1 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Maternal convulsions during pregnancy (empty)',
        'symptom': 's33',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (float)',
        'symptom': 's33',
        'child_2_1': '1.0',
        'endorsed': False,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (not endorsed)',
        'symptom': 's33',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (invalid-garbage)',
        'symptom': 's33',
        'child_2_1': '1 X',
        'endorsed': False,
    },
    {
        'sid': 'Maternal convulsions during pregnancy (invalid-out of range)',
        'symptom': 's33',
        'child_2_1': '1 47',
        'endorsed': False,
    },
    {
        'sid': 'Maternal hypertension during pregnancy',
        'symptom': 's34',
        'child_2_1': '2',
        'endorsed': True,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (multiple)',
        'symptom': 's34',
        'child_2_1': '3 2 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (duplicate)',
        'symptom': 's34',
        'child_2_1': '3 2 2 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (ignore constraint)',
        'symptom': 's34',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 2 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Maternal hypertension during pregnancy (empty)',
        'symptom': 's34',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (float)',
        'symptom': 's34',
        'child_2_1': '2.0',
        'endorsed': False,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (not endorsed)',
        'symptom': 's34',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (invalid-garbage)',
        'symptom': 's34',
        'child_2_1': '2 X',
        'endorsed': False,
    },
    {
        'sid': 'Maternal hypertension during pregnancy (invalid-out of range)',
        'symptom': 's34',
        'child_2_1': '2 47',
        'endorsed': False,
    },
    {
        'sid': 'Maternal anemiaduring pregnancy',
        'symptom': 's35',
        'child_2_1': '3',
        'endorsed': True,
    },
    {
        'sid': 'Maternal anemia during pregnancy (multiple)',
        'symptom': 's35',
        'child_2_1': '7 3 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal anemia during pregnancy (duplicate)',
        'symptom': 's35',
        'child_2_1': '7 3 3 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal anemia during pregnancy (ignore constraint)',
        'symptom': 's35',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 1 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Maternal anemia during pregnancy (empty)',
        'symptom': 's35',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Maternal anemia during pregnancy (float)',
        'symptom': 's35',
        'child_2_1': '3.0',
        'endorsed': False,
    },
    {
        'sid': 'Maternal anemia during pregnancy (not endorsed)',
        'symptom': 's35',
        'child_2_1': '1 5',
        'endorsed': False,
    },
    {
        'sid': 'Maternal anemia during pregnancy (invalid-garbage)',
        'symptom': 's35',
        'child_2_1': '3 X',
        'endorsed': False,
    },
    {
        'sid': 'Maternal anemia during pregnancy (invalid-out of range)',
        'symptom': 's35',
        'child_2_1': '3 47',
        'endorsed': False,
    },
    {
        'sid': 'Maternal diabetesduring pregnancy',
        'symptom': 's36',
        'child_2_1': '4',
        'endorsed': True,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (multiple)',
        'symptom': 's36',
        'child_2_1': '3 4 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (duplicate)',
        'symptom': 's36',
        'child_2_1': '3 4 4 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (ignore constraint)',
        'symptom': 's36',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 4 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Maternal diabetes during pregnancy (empty)',
        'symptom': 's36',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (float)',
        'symptom': 's36',
        'child_2_1': '4.0',
        'endorsed': False,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (not endorsed)',
        'symptom': 's36',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (invalid-garbage)',
        'symptom': 's36',
        'child_2_1': '4 X',
        'endorsed': False,
    },
    {
        'sid': 'Maternal diabetes during pregnancy (invalid-out of range)',
        'symptom': 's36',
        'child_2_1': '4 47',
        'endorsed': False,
    },
    {
        'sid': 'Delivered not head first',
        'symptom': 's37',
        'child_2_1': '5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered not head first (multiple)',
        'symptom': 's37',
        'child_2_1': '3 7 5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered not head first (duplicate)',
        'symptom': 's37',
        'child_2_1': '3 5 1 5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered not head first (ignore constraint)',
        'symptom': 's37',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 1 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Delivered not head first (empty)',
        'symptom': 's37',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Delivered not head first (float)',
        'symptom': 's37',
        'child_2_1': '5.0',
        'endorsed': False,
    },
    {
        'sid': 'Delivered not head first (not endorsed)',
        'symptom': 's37',
        'child_2_1': '3 7',
        'endorsed': False,
    },
    {
        'sid': 'Delivered not head first (invalid-garbage)',
        'symptom': 's37',
        'child_2_1': '5 X',
        'endorsed': False,
    },
    {
        'sid': 'Delivered not head first (invalid-out of range)',
        'symptom': 's37',
        'child_2_1': '5 47',
        'endorsed': False,
    },
    {
        'sid': 'Delivered cord first',
        'symptom': 's38',
        'child_2_1': '6',
        'endorsed': True,
    },
    {
        'sid': 'Delivered cord first (multiple)',
        'symptom': 's38',
        'child_2_1': '3 6 5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered cord first (duplicate)',
        'symptom': 's38',
        'child_2_1': '3 6 6 5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered cord first (ignore constraint)',
        'symptom': 's38',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 6 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Delivered cord first (empty)',
        'symptom': 's38',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Delivered cord first (float)',
        'symptom': 's38',
        'child_2_1': '6.0',
        'endorsed': False,
    },
    {
        'sid': 'Delivered cord first (not endorsed)',
        'symptom': 's38',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Delivered cord first (invalid-garbage)',
        'symptom': 's38',
        'child_2_1': '6 X',
        'endorsed': False,
    },
    {
        'sid': 'Delivered cord first (invalid-out of range)',
        'symptom': 's38',
        'child_2_1': '6 47',
        'endorsed': False,
    },
    {
        'sid': 'Delivered with cord around neck',
        'symptom': 's39',
        'child_2_1': '7',
        'endorsed': True,
    },
    {
        'sid': 'Delivered with cord around neck (multiple)',
        'symptom': 's39',
        'child_2_1': '3 7 5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered with cord around neck (duplicate)',
        'symptom': 's39',
        'child_2_1': '3 7 7 5',
        'endorsed': True,
    },
    {
        'sid': 'Delivered with cord around neck (ignore constraint)',
        'symptom': 's39',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 7 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Delivered with cord around neck (empty)',
        'symptom': 's39',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Delivered with cord around neck (float)',
        'symptom': 's39',
        'child_2_1': '7.0',
        'endorsed': False,
    },
    {
        'sid': 'Delivered with cord around neck (not endorsed)',
        'symptom': 's39',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Delivered with cord around neck (invalid-garbage)',
        'symptom': 's39',
        'child_2_1': '7 X',
        'endorsed': False,
    },
    {
        'sid': 'Delivered with cord around neck (invalid-out of range)',
        'symptom': 's39',
        'child_2_1': '7 47',
        'endorsed': False,
    },
    {
        'sid': 'Excessive bleeding during delivery',
        'symptom': 's40',
        'child_2_1': '8',
        'endorsed': True,
    },
    {
        'sid': 'Excessive bleeding during delivery (multiple)',
        'symptom': 's40',
        'child_2_1': '3 8 5',
        'endorsed': True,
    },
    {
        'sid': 'Excessive bleeding during delivery (duplicate)',
        'symptom': 's40',
        'child_2_1': '3 8 8 5',
        'endorsed': True,
    },
    {
        'sid': 'Excessive bleeding during delivery (ignore constraint)',
        'symptom': 's40',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 8 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Excessive bleeding during delivery (empty)',
        'symptom': 's40',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Excessive bleeding during delivery (float)',
        'symptom': 's40',
        'child_2_1': '8.0',
        'endorsed': False,
    },
    {
        'sid': 'Excessive bleeding during delivery (not endorsed)',
        'symptom': 's40',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Excessive bleeding during delivery (invalid-garbage)',
        'symptom': 's40',
        'child_2_1': '8 X',
        'endorsed': False,
    },
    {
        'sid': 'Excessive bleeding during delivery (invalid-out of range)',
        'symptom': 's40',
        'child_2_1': '8 47',
        'endorsed': False,
    },
    {
        'sid': 'Maternal fever during labor',
        'symptom': 's41',
        'child_2_1': '9',
        'endorsed': True,
    },
    {
        'sid': 'Maternal fever during labor (multiple)',
        'symptom': 's41',
        'child_2_1': '3 9 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal fever during labor (duplicate)',
        'symptom': 's41',
        'child_2_1': '3 9 9 5',
        'endorsed': True,
    },
    {
        'sid': 'Maternal fever during labor (ignore constraint)',
        'symptom': 's41',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 9 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Maternal fever during labor (empty)',
        'symptom': 's41',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Maternal fever during labor (float)',
        'symptom': 's41',
        'child_2_1': '9.0',
        'endorsed': False,
    },
    {
        'sid': 'Maternal fever during labor (not endorsed)',
        'symptom': 's41',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Maternal fever during labor (invalid-garbage)',
        'symptom': 's41',
        'child_2_1': '9 X',
        'endorsed': False,
    },
    {
        'sid': 'Maternal fever during labor (invalid-out of range)',
        'symptom': 's41',
        'child_2_1': '9 47',
        'endorsed': False,
    },
    {
        'sid': 'No pregnancy/delivery complications',
        'symptom': 's42',
        'child_2_1': '10',
        'endorsed': True,
    },
    {
        'sid': 'No pregnancy/delivery complications (multiple)',
        'symptom': 's42',
        'child_2_1': '3 10 5',
        'endorsed': True,
    },
    {
        'sid': 'No pregnancy/delivery complications (duplicate)',
        'symptom': 's42',
        'child_2_1': '3 10 10 5',
        'endorsed': True,
    },
    {
        'sid': 'No pregnancy/delivery complications (ignore constraint)',
        'symptom': 's42',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 10 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'No pregnancy/delivery complications (empty)',
        'symptom': 's42',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'No pregnancy/delivery complications (float)',
        'symptom': 's42',
        'child_2_1': '10.0',
        'endorsed': False,
    },
    {
        'sid': 'No pregnancy/delivery complications (not endorsed)',
        'symptom': 's42',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'No pregnancy/delivery complications (invalid-garbage)',
        'symptom': 's42',
        'child_2_1': '10 X',
        'endorsed': False,
    },
    {
        'sid': 'No pregnancy/delivery complications (invalid-out of range)',
        'symptom': 's42',
        'child_2_1': '10 47',
        'endorsed': False,
    },
    {
        'sid': 'Complications-don\'t know',
        'symptom': 's43',
        'child_2_1': '99',
        'endorsed': True,
    },
    {
        'sid': 'Complications-don\'t know (multiple)',
        'symptom': 's43',
        'child_2_1': '3 99 5',
        'endorsed': True,
    },
    {
        'sid': 'Complications-don\'t know (duplicate)',
        'symptom': 's43',
        'child_2_1': '3 99 99 5',
        'endorsed': True,
    },
    {
        'sid': 'Complications-don\'t know (ignore constraint)',
        'symptom': 's43',
        # Cannot have 10, 88 or 99 with other answers
        'child_2_1': '3 5 10 88 99',
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Complications-don\'t know (empty)',
        'symptom': 's43',
        'child_2_1': '',
        'endorsed': False,
    },
    {
        'sid': 'Complications-don\'t know (float)',
        'symptom': 's43',
        'child_2_1': '99.0',
        'endorsed': False,
    },
    {
        'sid': 'Complications-don\'t know (not endorsed)',
        'symptom': 's43',
        'child_2_1': '3 5',
        'endorsed': False,
    },
    {
        'sid': 'Complications-don\'t know (invalid-garbage)',
        'symptom': 's43',
        'child_2_1': '99 X',
        'endorsed': False,
    },
    {
        'sid': 'Complications-don\'t know (invalid-out of range)',
        'symptom': 's43',
        'child_2_1': '99 47',
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy duration (missing)',
        'symptom': 's47',
        'child_2_2': 9,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy duration (months-yes)',
        'symptom': 's45',
        'child_2_2': 2,
        'child_2_2a': 9,
        'endorsed': True,
    },
    {
        'sid': 'Pregnancy duration (months-no)',
        'symptom': 's45',
        'child_2_2': 2,
        'child_2_2a': 8,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy duration (threshold)',
        'symptom': 's45',
        'child_2_2': 2,
        'child_2_2a': 8.5,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Pregnancy duration (months-no-empty)',
        'symptom': 's45',
        'child_2_2': 2,
        'child_2_2a': '',
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy duration (months-no-invalid)',
        'symptom': 's45',
        'child_2_2': 2,
        'child_2_2a': 8,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy duration (months-no-no unit)',
        'symptom': 's45',
        'child_2_2': '',
        'child_2_2a': 9,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy duration (float)',
        'symptom': 's45',
        'child_2_2': 2,
        'child_2_2a': 9.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Pregnancy ended early (early)',
        'symptom': 's46991',
        'child_2_3': 1,
        'endorsed': True,
    },
    {
        'sid': 'Pregnancy ended early (on time)',
        'symptom': 's46991',
        'child_2_3': 2,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy ended early (late)',
        'symptom': 's46991',
        'child_2_3': 3,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy ended early (missing)',
        'symptom': 's46991',
        'child_2_3': 9,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy ended late (early)',
        'symptom': 's46992',
        'child_2_3': 1,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy ended late (on time)',
        'symptom': 's46992',
        'child_2_3': 2,
        'endorsed': False,
    },
    {
        'sid': 'Pregnancy ended late (late)',
        'symptom': 's46992',
        'child_2_3': 3,
        'endorsed': True,
    },
    {
        'sid': 'Pregnancy ended late (missing)',
        'symptom': 's46992',
        'child_2_3': 9,
        'endorsed': False,
    },
    {
        'sid': 'Baby moving in last few days of pregnancy',
        'symptom': 's47',
        'child_2_4': 1
    },
    {
        'sid': 'Last feel baby move (missing)',
        'symptom': 's48',
        'child_2_5': 9,
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (hours-yes)',
        'symptom': 's48',
        'child_2_5': 5,
        'child_2_5a': 9,
        'endorsed': True,
    },
    {
        'sid': 'Last feel baby move (hours-no)',
        'symptom': 's48',
        'child_2_5': 5,
        'child_2_5a': 2,
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (hours-no-empty)',
        'symptom': 's48',
        'child_2_5': 5,
        'child_2_5a': '',
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (hours-no-invalid)',
        'symptom': 's48',
        'child_2_5': 5,
        'child_2_5a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (hours-no-no unit)',
        'symptom': 's48',
        'child_2_5': '',
        'child_2_5a': 9,
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (days-yes)',
        'symptom': 's48',
        'child_2_5': 4,
        'child_2_5b': 9,
        'endorsed': True,
    },
    {
        'sid': 'Last feel baby move (days-no)',
        'symptom': 's48',
        'child_2_5': 4,
        'child_2_5b': 0,
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (days-no-empty)',
        'symptom': 's48',
        'child_2_5': 4,
        'child_2_5b': '',
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (days-no-invalid)',
        'symptom': 's48',
        'child_2_5': 4,
        'child_2_5b': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (days-no-no unit)',
        'symptom': 's48',
        'child_2_5': '',
        'child_2_5b': 9,
        'endorsed': False,
    },
    {
        'sid': 'Last feel baby move (threshold)',
        'symptom': 's48',
        'child_2_5': 5,
        'child_2_5a': 3,
        'endorsed': True,
    },
    {
        'sid': 'Last feel baby move (float)',
        'symptom': 's48',
        'child_2_5': 2,
        'child_2_5a': 9.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Water broke during labor (before)',
        'symptom': 's49991',
        'child_2_6': 1,
        'endorsed': False,
    },
    {
        'sid': 'Water broke during labor (during)',
        'symptom': 's49991',
        'child_2_6': 2,
        'endorsed': True,
    },
    {
        'sid': 'Water broke during labor (missing)',
        'symptom': 's49991',
        'child_2_6': 9,
        'endorsed': False,
    },
    {
        'sid': 'Water broke more than a day before labor (less than 1 day)',
        'symptom': 's50991',
        'child_2_7': 1,
        'endorsed': False,
    },
    {
        'sid': 'Water broke more than a day before labor (one day or more)',
        'symptom': 's50991',
        'child_2_7': 2,
        'endorsed': True,
    },
    {
        'sid': 'Water broke more than a day before labor (missing)',
        'symptom': 's50991',
        'child_2_7': 9,
        'endorsed': False,
    },
    {
        'sid': 'Delivery liquor not clear (green)',
        'symptom': 's51991',
        'child_2_8': 1,
        'endorsed': True,
    },
    {
        'sid': 'Delivery liquor not clear (clear)',
        'symptom': 's51991',
        'child_2_8': 2,
        'endorsed': False,
    },
    {
        'sid': 'Delivery liquor not clear (other)',
        'symptom': 's51991',
        'child_2_8': 3,
        'endorsed': True,
    },
    {
        'sid': 'Delivery liquor not clear (missing)',
        'symptom': 's51991',
        'child_2_8': 9,
        'endorsed': False,
    },
    {
        'sid': 'Delivery liquor foul smelling',
        'symptom': 's52',
        'child_2_9': 1
    },
    {
        'sid': 'Delivery duration (missing)',
        'symptom': 's53',
        'child_2_10': 9,
        'endorsed': False,
    },
    {
        'sid': 'Delivery duration (hours-yes)',
        'symptom': 's53',
        'child_2_10': 5,
        'child_2_10a': 6,
        'endorsed': True,
    },
    {
        'sid': 'Delivery duration (hours-no)',
        'symptom': 's53',
        'child_2_10': 5,
        'child_2_10a': 4,
        'endorsed': False,
    },
    {
        'sid': 'Delivery duration (threshold)',
        'symptom': 's53',
        'child_2_10': 5,
        'child_2_10a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Delivery duration (hours-no-empty)',
        'symptom': 's53',
        'child_2_10': 5,
        'child_2_10a': '',
        'endorsed': False,
    },
    {
        'sid': 'Delivery duration (hours-no-invalid)',
        'symptom': 's53',
        'child_2_10': 5,
        'child_2_10a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Delivery duration (hours-no-no unit)',
        'symptom': 's53',
        'child_2_10': '',
        'child_2_10a': 6,
        'endorsed': False,
    },
    {
        'sid': 'Delivery duration (float)',
        'symptom': 's53',
        'child_2_10': 5,
        'child_2_10a': 9.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Mother received vaccinations during pregnancy',
        'symptom': 's54',
        'child_2_11': 1
    },
    {
        'sid': 'Incomplete vaccination doses (one)',
        'symptom': 's55991',
        'child_2_12': 1,
        'endorsed': True,
    },
    {
        'sid': 'Incomplete vaccination doses (two)',
        'symptom': 's55991',
        'child_2_12': 2,
        'endorsed': True,
    },
    {
        'sid': 'Incomplete vaccination doses (three)',
        'symptom': 's55991',
        'child_2_12': 3,
        'endorsed': False,
    },
    {
        'sid': 'Incomplete vaccination doses (four)',
        'symptom': 's55991',
        'child_2_12': 4,
        'endorsed': False,
    },
    {
        'sid': 'Incomplete vaccination doses (five)',
        'symptom': 's55991',
        'child_2_12': 5,
        'endorsed': False,
    },
    {
        'sid': 'Incomplete vaccination doses (missing)',
        'symptom': 's55991',
        'child_2_12': 9,
        'endorsed': False,
    },
    # s56 contains information pertaining to delivery location that
    # duplicates information in s11991
    {
        'sid': 'Non-medical birth attendant (doctor)',
        'symptom': 's57991',
        'child_2_15': 1,
        'endorsed': False,
    },
    {
        'sid': 'Non-medical birth attendant (nurse/midwife)',
        'symptom': 's57991',
        'child_2_15': 2,
        'endorsed': False,
    },
    {
        'sid': 'Non-medical birth attendant (relative)',
        'symptom': 's57991',
        'child_2_15': 3,
        'endorsed': True,
    },
    {
        'sid': 'Non-medical birth attendant (self)',
        'symptom': 's57991',
        'child_2_15': 4,
        'endorsed': True,
    },
    {
        'sid': 'Non-medical birth attendant (traditional birth attendant)',
        'symptom': 's57991',
        'child_2_15': 5,
        'endorsed': True,
    },
    {
        'sid': 'Non-medical birth attendant (other)',
        'symptom': 's57991',
        'child_2_15': 6,
        'endorsed': True,
    },
    {
        'sid': 'Non-medical birth attendant (refused)',
        'symptom': 's57991',
        'child_2_15': 8,
        'endorsed': True,
    },
    {
        'sid': 'Non-medical birth attendant (don\'t know)',
        'symptom': 's57991',
        'child_2_15': 9,
        'endorsed': True,
    },
    {
        'sid': 'Delivery type-vaginal w/ foreceps (vaginal w/ foreceps)',
        'symptom': 's58991',
        'child_2_17': 1,
        'endorsed': True,
    },
    {
        'sid': 'Delivery type-vaginal w/ foreceps (vaginal w/o foreceps)',
        'symptom': 's58991',
        'child_2_17': 2,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/ foreceps (vaginal, unspecified)',
        'symptom': 's58991',
        'child_2_17': 3,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/ foreceps (c-section)',
        'symptom': 's58991',
        'child_2_17': 4,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/ foreceps (missing)',
        'symptom': 's58991',
        'child_2_17': 9,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/o foreceps (vaginal w/ foreceps)',
        'symptom': 's58992',
        'child_2_17': 1,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/o foreceps (vaginal w/o foreceps)',
        'symptom': 's58992',
        'child_2_17': 2,
        'endorsed': True,
    },
    {
        'sid': 'Delivery type-vaginal w/o foreceps (vaginal, unspecified)',
        'symptom': 's58992',
        'child_2_17': 3,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/o foreceps (c-section)',
        'symptom': 's58992',
        'child_2_17': 4,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal w/o foreceps (missing)',
        'symptom': 's58992',
        'child_2_17': 9,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal, unspecified (vaginal w/ foreceps)',
        'symptom': 's58993',
        'child_2_17': 1,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal, unspecified (vaginal w/o foreceps)',
        'symptom': 's58993',
        'child_2_17': 2,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal, unspecified (vaginal, unspecified)',
        'symptom': 's58993',
        'child_2_17': 3,
        'endorsed': True,
    },
    {
        'sid': 'Delivery type-vaginal, unspecified (c-section)',
        'symptom': 's58993',
        'child_2_17': 4,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-vaginal, unspecified (missing)',
        'symptom': 's58993',
        'child_2_17': 9,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-c-section (vaginal w/ foreceps)',
        'symptom': 's58994',
        'child_2_17': 1,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-c-section (vaginal w/o foreceps)',
        'symptom': 's58994',
        'child_2_17': 2,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-c-section (vaginal, unspecified)',
        'symptom': 's58994',
        'child_2_17': 3,
        'endorsed': False,
    },
    {
        'sid': 'Delivery type-c-section (c-section)',
        'symptom': 's58994',
        'child_2_17': 4,
        'endorsed': True,
    },
    {
        'sid': 'Delivery type-c-section (missing)',
        'symptom': 's58994',
        'child_2_17': 9,
        'endorsed': False,
    },
    {
        'sid': 'Received injection during labor before delivery',
        'symptom': 's59',
        'child_2_18': 1
    },
    {
        'sid': 'Bruises when born',
        'symptom': 's60',
        'child_3_1': 1
    },
    {
        'sid': 'Any abnormalities',
        'symptom': 's61',
        'child_3_2': 1
    },
    {
        'sid': 'Head very small',
        'symptom': 's62',
        'child_3_3': '1',
        'endorsed': True,
    },
    {
        'sid': 'Head very small (multiple)',
        'symptom': 's62',
        'child_3_3': '11 1 3',
        'endorsed': True,
    },
    {
        'sid': 'Head very small (duplicate)',
        'symptom': 's62',
        'child_3_3': '11 1 3 1',
        'endorsed': True,
    },
    {
        'sid': 'Head very small (ignore constraint)',
        'symptom': 's62',
        'child_3_3': '11 1 3 8',  # Cannot have 8 with other answers
        'endorsed': True,   # but we ignore ODK constraints
    },
    {
        'sid': 'Head very small (empty)',
        'symptom': 's62',
        'child_3_3': '',
        'endorsed': False,
    },
    {
        'sid': 'Head very small (float)',
        'symptom': 's62',
        'child_3_3': '1.0',
        'endorsed': False,
    },
    {
        'sid': 'Head very small (not endorsed)',
        'symptom': 's62',
        'child_3_3': '2 11',
        'endorsed': False,
    },
    {
        'sid': 'Head very small (invalid-garbage)',
        'symptom': 's62',
        'child_3_3': '1 X',
        'endorsed': False,
    },
    {
        'sid': 'Head very small (invalid-out of range)',
        'symptom': 's62',
        'child_3_3': '1 47',
        'endorsed': False,
    },
    {
        'sid': 'Head very large',
        'symptom': 's63',
        'child_3_3': '2',
        'endorsed': True,
    },
    {
        'sid': 'Head very large (multiple)',
        'symptom': 's63',
        'child_3_3': '11 2 3',
        'endorsed': True,
    },
    {
        'sid': 'Head very large (duplicate)',
        'symptom': 's63',
        'child_3_3': '11 2 3 2',
        'endorsed': True,
    },
    {
        'sid': 'Head very large (ignore constraint)',
        'symptom': 's63',
        'child_3_3': '11 2 3 8',  # Cannot have 8 with other answers
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Head very large (empty)',
        'symptom': 's63',
        'child_3_3': '',
        'endorsed': False,
    },
    {
        'sid': 'Head very large (float)',
        'symptom': 's63',
        'child_3_3': '2.0',
        'endorsed': False,
    },
    {
        'sid': 'Head very large (not endorsed)',
        'symptom': 's63',
        'child_3_3': '1 11',
        'endorsed': False,
    },
    {
        'sid': 'Head very large (invalid-garbage)',
        'symptom': 's63',
        'child_3_3': '2 X',
        'endorsed': False,
    },
    {
        'sid': 'Head very large (invalid-out of range)',
        'symptom': 's63',
        'child_3_3': '2 47',
        'endorsed': False,
    },
    {
        'sid': 'Mass on back of head/neck',
        'symptom': 's64',
        'child_3_3': '3',
        'endorsed': True,
    },
    {
        'sid': 'Mass on back of head/neck (multiple)',
        'symptom': 's64',
        'child_3_3': '11 1 3',
        'endorsed': True,
    },
    {
        'sid': 'Mass on back of head/neck (duplicate)',
        'symptom': 's64',
        'child_3_3': '11 3 3 1',
        'endorsed': True,
    },
    {
        'sid': 'Mass on back of head/neck (ignore constraint)',
        'symptom': 's64',
        'child_3_3': '11 1 3 8',  # Cannot have 8 with other answers
        'endorsed': True,  # but we ignore ODK constraints
    },
    {
        'sid': 'Mass on back of head/neck (empty)',
        'symptom': 's64',
        'child_3_3': '',
        'endorsed': False,
    },
    {
        'sid': 'Mass on back of head/neck (float)',
        'symptom': 's64',
        'child_3_3': '3.0',
        'endorsed': False,
    },
    {
        'sid': 'Mass on back of head/neck (not endorsed)',
        'symptom': 's64',
        'child_3_3': ' 2 11',
        'endorsed': False,
    },
    {
        'sid': 'Mass on back of head/neck (invalid-garbage)',
        'symptom': 's64',
        'child_3_3': '3 X',
        'endorsed': False,
    },
    {
        'sid': 'Mass on back of head/neck (invalid-out of range)',
        'symptom': 's64',
        'child_3_3': '3 47',
        'endorsed': False,
    },
    {
        'sid': 'Breathe immediately after birth',
        'symptom': 's65',
        'child_3_4': 1
    },
    {
        'sid': 'Difficulty breathing',
        'symptom': 's66',
        'child_3_5': 1
    },
    {
        'sid': 'Breathing assistance given',
        'symptom': 's67',
        'child_3_6': 1
    },
    {
        'sid': 'Cried immediately after birth',
        'symptom': 's68',
        'child_3_7': 1
    },
    {
        'sid': 'Did not cry within 30 minutes of birth (within 5 minutes)',
        'symptom': 's69991',
        'child_3_8': 1,
        'endorsed': False,
    },
    {
        'sid': 'Did not cry within 30 minutes of birth (within 30 minutes)',
        'symptom': 's69991',
        'child_3_8': 2,
        'endorsed': False,
    },
    {
        'sid': 'Did not cry within 30 minutes of birth (more than 30 minutes)',
        'symptom': 's69991',
        'child_3_8': 3,
        'endorsed': True,
    },
    {
        'sid': 'Did not cry within 30 minutes of birth (never)',
        'symptom': 's69991',
        'child_3_8': 4,
        'endorsed': True,
    },
    {
        'sid': 'Did not cry within 30 minutes of birth (missing)',
        'symptom': 's69991',
        'child_3_8': 9,
        'endorsed': False,
    },
    {
        'sid': 'Stopped being able to cry',
        'symptom': 's70',
        'child_3_9': 1
    },
    {
        'sid': 'Stopped crying 1 day before death (less than 1 day)',
        'symptom': 's71991',
        'child_3_10': 1,
        'endorsed': False,
    },
    {
        'sid': 'Stopped crying 1 day before death (1 day or more)',
        'symptom': 's71991',
        'child_3_10': 2,
        'endorsed': True,
    },
    {
        'sid': 'Stopped crying 1 day before death (missing)',
        'symptom': 's71991',
        'child_3_10': 9,
        'endorsed': False,
    },
    {
        'sid': 'Suckled normal on first day of life',
        'symptom': 's72',
        'child_3_11': 1
    },
    {
        'sid': 'Suckled normally ever',
        'symptom': 's73',
        'child_3_12': 1
    },
    {
        'sid': 'Stopped being able to suckle',
        'symptom': 's74',
        'child_3_13': 1
    },
    {
        'sid': 'Stopped being able to suckle duration (missing)',
        'symptom': 's75',
        'child_3_14': 9,
        'endorsed': False,
    },
    {
        'sid': 'Stopped being able to suckle duration (days-yes)',
        'symptom': 's75',
        'child_3_14': 4,
        'child_3_14a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Stopped being able to suckle duration (days-no)',
        'symptom': 's75',
        'child_3_14': 4,
        'child_3_14a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Stopped being able to suckle duration (days-threshold)',
        'symptom': 's75',
        'child_3_14': 4,
        'child_3_14a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Stopped being able to suckle duration (days-no-empty)',
        'symptom': 's75',
        'child_3_14': 4,
        'child_3_14a': '',
        'endorsed': False,
    },
    {
        'sid': 'Stopped being able to suckle duration (days-no-invalid)',
        'symptom': 's75',
        'child_3_14': 4,
        'child_3_14a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Stopped being able to suckle duration (days-no-no unit)',
        'symptom': 's75',
        'child_3_14': '',
        'child_3_14a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Stopped being able to suckle duration (float)',
        'symptom': 's75',
        'child_3_14': 4,
        'child_3_14a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Stopped suckling a day before death (less than 1 day)',
        'symptom': 's76991',
        'child_3_15': 1,
        'endorsed': False,
    },
    {
        'sid': 'Stopped suckling a day before death (1 day or more)',
        'symptom': 's76991',
        'child_3_15': 2,
        'endorsed': True,
    },
    {
        'sid': 'Stopped suckling a day before death (missing)',
        'symptom': 's76991',
        'child_3_15': 9,
        'endorsed': False,
    },
    {
        'sid': 'Able to open mouth when stopped suckling',
        'symptom': 's77',
        'child_3_16': 1
    },
    {
        'sid': 'Difficult breathing',
        'symptom': 's78',
        'child_3_17': 1
    },
    {
        'sid': 'Age difficult breathing started (missing)',
        'symptom': 's79',
        'child_3_18': 9,
        'endorsed': False,
    },
    {
        'sid': 'Age difficult breathing started (days-yes)',
        'symptom': 's79',
        'child_3_18': 4,
        'child_3_18a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Age difficult breathing started (days-no)',
        'symptom': 's79',
        'child_3_18': 4,
        'child_3_18a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age difficult breathing started (days-threshold)',
        'symptom': 's79',
        'child_3_18': 4,
        'child_3_18a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Age difficult breathing started (days-no-empty)',
        'symptom': 's79',
        'child_3_18': 4,
        'child_3_18a': '',
        'endorsed': False,
    },
    {
        'sid': 'Age difficult breathing started (days-no-invalid)',
        'symptom': 's79',
        'child_3_18': 4,
        'child_3_18a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age difficult breathing started (days-no-no unit)',
        'symptom': 's79',
        'child_3_18': '',
        'child_3_18a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Age difficult breathing started (float)',
        'symptom': 's79',
        'child_3_18': 4,
        'child_3_18a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Difficult breathing duration (missing)',
        'symptom': 's80',
        'child_3_19': 9,
        'endorsed': False,
    },
    {
        'sid': 'Difficult breathing duration (days-yes)',
        'symptom': 's80',
        'child_3_19': 4,
        'child_3_19a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Difficult breathing duration (days-no)',
        'symptom': 's80',
        'child_3_19': 4,
        'child_3_19a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Difficult breathing duration (days-threshold)',
        'symptom': 's80',
        'child_3_19': 4,
        'child_3_19a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Difficult breathing duration (days-no-empty)',
        'symptom': 's80',
        'child_3_19': 4,
        'child_3_19a': '',
        'endorsed': False,
    },
    {
        'sid': 'Difficult breathing duration (days-no-invalid)',
        'symptom': 's80',
        'child_3_19': 4,
        'child_3_19a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Difficult breathing duration (days-no-no unit)',
        'symptom': 's80',
        'child_3_19': '',
        'child_3_19a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Difficult breathing duration (float)',
        'symptom': 's80',
        'child_3_19': 4,
        'child_3_19a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Fast breathing',
        'symptom': 's81',
        'child_3_20': 1
    },
    {
        'sid': 'Age fast breathing started (missing)',
        'symptom': 's82',
        'child_3_21': 9,
        'endorsed': False,
    },
    {
        'sid': 'Age fast breathing started (days-yes)',
        'symptom': 's82',
        'child_3_21': 4,
        'child_3_21a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Age fast breathing started (days-no)',
        'symptom': 's82',
        'child_3_21': 4,
        'child_3_21a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age fast breathing started (days-threshold)',
        'symptom': 's82',
        'child_3_21': 4,
        'child_3_21a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Age fast breathing started (days-no-empty)',
        'symptom': 's82',
        'child_3_21': 4,
        'child_3_21a': '',
        'endorsed': False,
    },
    {
        'sid': 'Age fast breathing started (days-no-invalid)',
        'symptom': 's82',
        'child_3_21': 4,
        'child_3_21a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age fast breathing started (days-no-no unit)',
        'symptom': 's82',
        'child_3_21': '',
        'child_3_21a': 4,
        'endorsed': False,
    },
    {
        'sid': 'Age fast breathing started (float)',
        'symptom': 's82',
        'child_3_21': 4,
        'child_3_21a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Fast breathing duration (missing)',
        'symptom': 's83',
        'child_3_22': 9,
        'endorsed': False,
    },
    {
        'sid': 'Fast breathing duration (days-yes)',
        'symptom': 's83',
        'child_3_22': 4,
        'child_3_22a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Fast breathing duration (days-no)',
        'symptom': 's83',
        'child_3_22': 4,
        'child_3_22a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Fast breathing duration (days-threshold)',
        'symptom': 's83',
        'child_3_22': 4,
        'child_3_22a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Fast breathing duration (days-no-empty)',
        'symptom': 's83',
        'child_3_22': 4,
        'child_3_22a': '',
        'endorsed': False,
    },
    {
        'sid': 'Fast breathing duration (days-no-invalid)',
        'symptom': 's83',
        'child_3_22': 4,
        'child_3_22a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Fast breathing duration (days-no-no unit)',
        'symptom': 's83',
        'child_3_22': '',
        'child_3_22a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Fast breathing duration (float)',
        'symptom': 's83',
        'child_3_22': 4,
        'child_3_22a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Indrawing chest',
        'symptom': 's84',
        'child_3_23': 1
    },
    {
        'sid': 'Grunting',
        'symptom': 's85',
        'child_3_24': 1
    },
    {
        'sid': 'Convulsions',
        'symptom': 's86',
        'child_3_25': 1
    },
    {
        'sid': 'Fever',
        'symptom': 's87',
        'child_3_26': 1
    },
    {
        'sid': 'Age fever started (missing)',
        'symptom': 's88',
        'child_3_27': 9,
        'endorsed': False,
    },
    {
        'sid': 'Age fever started (days-yes)',
        'symptom': 's88',
        'child_3_27': 4,
        'child_3_27a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Age fever started (days-no)',
        'symptom': 's88',
        'child_3_27': 4,
        'child_3_27a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age fever started (days-threshold)',
        'symptom': 's88',
        'child_3_27': 4,
        'child_3_27a': 3,
        'endorsed': True,
    },
    {
        'sid': 'Age fever started (days-no-empty)',
        'symptom': 's88',
        'child_3_27': 4,
        'child_3_27a': '',
        'endorsed': False,
    },
    {
        'sid': 'Age fever started (days-no-invalid)',
        'symptom': 's88',
        'child_3_27': 4,
        'child_3_27a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age fever started (days-no-no unit)',
        'symptom': 's88',
        'child_3_27': '',
        'child_3_27a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Age fever started (float)',
        'symptom': 's88',
        'child_3_27': 4,
        'child_3_27a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Fever duration (missing)',
        'symptom': 's89',
        'child_3_28': 9,
        'endorsed': False,
    },
    {
        'sid': 'Fever duration (days-yes)',
        'symptom': 's89',
        'child_3_28': 4,
        'child_3_28a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Fever duration (days-no)',
        'symptom': 's89',
        'child_3_28': 4,
        'child_3_28a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Fever duration (days-threshold)',
        'symptom': 's89',
        'child_3_28': 4,
        'child_3_28a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Fever duration (days-no-empty)',
        'symptom': 's89',
        'child_3_28': 4,
        'child_3_28a': '',
        'endorsed': False,
    },
    {
        'sid': 'Fever duration (days-no-invalid)',
        'symptom': 's89',
        'child_3_28': 4,
        'child_3_28a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Fever duration (days-no-no unit)',
        'symptom': 's89',
        'child_3_28': '',
        'child_3_28a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Fever duration (float)',
        'symptom': 's89',
        'child_3_28': 4,
        'child_3_28a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Became cold to touch',
        'symptom': 's90',
        'child_3_29': 1
    },
    {
        'sid': 'Age became cold to touch (missing)',
        'symptom': 's91',
        'child_3_30': 9,
        'endorsed': False,
    },
    {
        'sid': 'Age became cold to touch (days-yes)',
        'symptom': 's91',
        'child_3_30': 4,
        'child_3_30a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Age became cold to touch (days-no)',
        'symptom': 's91',
        'child_3_30': 4,
        'child_3_30a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Age became cold to touch (days-threshold)',
        'symptom': 's91',
        'child_3_30': 4,
        'child_3_30a': 3,
        'endorsed': True,
    },
    {
        'sid': 'Age became cold to touch (days-no-empty)',
        'symptom': 's91',
        'child_3_30': 4,
        'child_3_30a': '',
        'endorsed': False,
    },
    {
        'sid': 'Age became cold to touch (days-no-invalid)',
        'symptom': 's91',
        'child_3_30': 4,
        'child_3_30a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Age became cold to touch (days-no-no unit)',
        'symptom': 's91',
        'child_3_30': '',
        'child_3_30a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Age became cold to touch (float)',
        'symptom': 's91',
        'child_3_30': 4,
        'child_3_30a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Cold to touch duration (missing)',
        'symptom': 's92',
        'child_3_31': 9,
        'endorsed': False,
    },
    {
        'sid': 'Cold to touch duration (days-yes)',
        'symptom': 's92',
        'child_3_31': 4,
        'child_3_31a': 5,
        'endorsed': True,
    },
    {
        'sid': 'Cold to touch duration (days-no)',
        'symptom': 's92',
        'child_3_31': 4,
        'child_3_31a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Cold to touch duration (days-threshold)',
        'symptom': 's92',
        'child_3_31': 4,
        'child_3_31a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Cold to touch duration (days-no-empty)',
        'symptom': 's92',
        'child_3_31': 4,
        'child_3_31a': '',
        'endorsed': False,
    },
    {
        'sid': 'Cold to touch duration (days-no-invalid)',
        'symptom': 's92',
        'child_3_31': 4,
        'child_3_31a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Cold to touch duration (days-no-no unit)',
        'symptom': 's92',
        'child_3_31': '',
        'child_3_31a': 5,
        'endorsed': False,
    },
    {
        'sid': 'Cold to touch duration (float)',
        'symptom': 's92',
        'child_3_31': 4,
        'child_3_31a': 5.2,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Became lethargic',
        'symptom': 's93',
        'child_3_32': 1
    },
    {
        'sid': 'Became unresponsive/unconscious',
        'symptom': 's94',
        'child_3_33': 1
    },
    {
        'sid': 'Bulging fontanelle',
        'symptom': 's95',
        'child_3_34': 1
    },
    {
        'sid': 'Pus from umbilical cord stump',
        'symptom': 's96',
        'child_3_35': 1
    },
    {
        'sid': 'Redness at umbilical cord stump',
        'symptom': 's97',
        'child_3_36': 1
    },
    {
        'sid': 'Umbilical cord redness spread to abdomin',
        'symptom': 's98',
        'child_3_37': 1
    },
    {
        'sid': 'Skin bumps containing pus',
        'symptom': 's99',
        'child_3_38': 1
    },
    {
        'sid': 'Ulcers',
        'symptom': 's100',
        'child_3_39': 1
    },
    {
        'sid': 'Skin redness or swelling',
        'symptom': 's101',
        'child_3_40': 1
    },
    {
        'sid': 'Skin turned black',
        'symptom': 's102',
        'child_3_41': 1
    },
    {
        'sid': 'Bled',
        'symptom': 's103',
        'child_3_42': 1
    },
    {
        'sid': 'Diarrhea',
        'symptom': 's104',
        'child_3_44': 1
    },
    {
        'sid': 'Number of stools (zero)',
        'symptom': 's105',
        'child_3_45a': 0,
        'endorsed': False,
    },
    {
        'sid': 'Number of stools (one)',
        'symptom': 's105',
        'child_3_45a': 1,
        'endorsed': False,
    },
    {
        'sid': 'Number of stools (two)',
        'symptom': 's105',
        'child_3_45a': 2,
        'endorsed': True,
    },
    {
        'sid': 'Number of stools (three)',
        'symptom': 's105',
        'child_3_45a': 3,
        'endorsed': True,
    },
    {
        'sid': 'Number of stools (float)',
        'symptom': 's105',
        'child_3_45a': 2.5,
        'endorsed': False,  # only integers are valid
    },
    {
        'sid': 'Number of stools (empty)',
        'symptom': 's105',
        'child_3_45a': '',
        'endorsed': False,
    },
    {
        'sid': 'Number of stools (invalid)',
        'symptom': 's105',
        'child_3_45a': 'XXX',
        'endorsed': False,
    },
    {
        'sid': 'Vomitting',
        'symptom': 's106',
        'child_3_46': 1
    },
    {
        'sid': 'Yellow skin',
        'symptom': 's107',
        'child_3_47': 1
    },
    {
        'sid': 'Yellow eyes',
        'symptom': 's108',
        'child_3_48': 1
    },
    {
        'sid': 'Appear healthy and die suddenly',
        'symptom': 's109',
        'child_3_49': 1
    },
    {
        'sid': 'Mother ever tested for HIV',
        'symptom': 's188',
        'child_5_17': 1
    },
    {
        'sid': 'Mother tested positive for HIV',
        'symptom': 's189',
        'child_5_18': 1
    },
    {
        'sid': 'Mother told she had HIV by health worker',
        'symptom': 's190',
        'child_5_19': 1
    },
    {
        'sid': 'Sex',
        'symptom': 'sex',
        'gen_5_2': 1,
        'endorsed': False,
    },
    {
        'sid': 'Sex',
        'symptom': 'sex',
        'gen_5_2': 2,
        'endorsed': True,
    },
    {
        'sid': 'Sex',
        'symptom': 'sex',
        'gen_5_2': 9,
        'endorsed': False,
    },
    {
        'sid': 'Sex',
        'symptom': 'sex',
        'gen_5_2': '',
        'endorsed': False,
    },
    ###
    #  Under-weight symptoms
    #  These compare the weight at the last medical exam after birth to a
    #  standard growth curve. The curve is age/sex dependent.
    #
    #  The ages used for the weight by age thresholds are truncated months.
    #  For neonates the only possible age is zero months
    #
    #  We calculate age from birth date and exam date, since the age at last
    #  exam is likely less than the age at death.
    ###
    # TODO: comprehensive coverage of under weight symptoms
    {
        'sid': 'Underweight 3 SD, male age 0 months',
        'symptom': 's180',
        # Birth date
        'gen_5_1a': 2000,  # year
        'gen_5_1b': 1,  # January
        'gen_5_1c': 1,  # day
        'gen_5_2': 1,  # male
        # Examine date (15 days later)
        'child_5_6b': 2000,  # year
        'child_5_6c': 1,  # January
        'child_5_6d': 15,  # day
        # Weight
        'child_5_6e': 1,  # grams as unit
        'child_5_6f': 1000,  # weight is grams
        'endorsed': True,
    },
    {
        'sid': 'Underweight 2 SD, male age 0 months',
        'symptom': 's181',
        # Birth date
        'gen_5_1a': 2000,    # year
        'gen_5_1b': 1,       # January
        'gen_5_1c': 1,       # day
        'gen_5_2': 1,        # male
        # Examine date (15 days later)
        'child_5_6b': 2000,  # year
        'child_5_6c': 1,     # January
        'child_5_6d': 15,    # day
        # Weight
        'child_5_6e': 1,     # grams as unit
        'child_5_6f': 1000,  # weight is grams
        'endorsed': True,
    },
]

for case in MAPPING:
    if 'endorsed' not in case and len(case) == 3:
        key = [k for k in case if k not in ('sid', 'symptom')][0]
        if case[key] == 1:
            MAPPING.extend([
                {
                    'sid': '{} ({})'.format(case['sid'], null),
                    'symptom': case['symptom'],
                    key: value,
                    'endorsed': False,
                }
                for null, value in list({'missing': 9, 'no': 0, 'empty': ''}.items())
            ])
