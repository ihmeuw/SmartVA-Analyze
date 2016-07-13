import random

RULE_NAME = 'Sometimes True'

CAUSE_ID = 3

random.seed(0)


def logic_rule(row):
    return random.randint(0, 2) == 0
