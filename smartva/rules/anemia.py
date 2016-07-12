RULE_NAME = 'Anemia'

CAUSE_ID = 3


def logic_rule(row):
    symptom_value = 0

    if (row['g5_02'] == 2  # sex
            and 12 < row['g5_04a'] <= 49  # age
            and row['a3_10'] == 1  # pregnant
            and (row['a3_07'] == 1 and row['a3_08'] > 90)  # overdue
            and (row['a3_17'] == 1 or row['a3_18'] == 1)):  # postpartum

        symptom_value += int(row['a2_20'] == 1)  # pale
        symptom_value += int(row['a2_37'] == 1 or row['a2_40'] == 1)  # breathing
        symptom_value += int(row['a2_43'] == 1)  # chest_pain
        symptom_value += int(row['a2_69'] == 1)  # headaches

    return symptom_value >= 3
