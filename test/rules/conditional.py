RULE_NAME = 'Conditional'

CAUSE_ID = 2


def logic_rule(row, condition='condition'):
    return bool(int(row[condition]))
