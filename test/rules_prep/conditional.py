RULE_NAME = 'Conditional'

CAUSE_ID = 1002


def logic_rule(row, condition='condition'):
    return bool(int(row[condition])) and CAUSE_ID
