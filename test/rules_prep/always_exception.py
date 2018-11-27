RULE_NAME = 'Always Exception'

CAUSE_ID = 1004


def logic_rule(row):
    raise KeyError('0')
    return True
