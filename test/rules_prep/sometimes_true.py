import random

RULE_NAME = 'Sometimes True'

CAUSE_ID = 1003

# random.seed(0) # FIXME: this random value changed from python 2 to python 3, leading the test to fail
# HACK: copy the random stream from python 2 into a list, to replicate the random stream from python 2 for testing purposes
_random_randint_0_2_py2_stream = [2, 2, 1, 0, 1, 1, 2, 0, 1, 1]  # list generated in python2 with `random.seed(0); [random.randint(0, 2) for _ in range(10)]`
_py2_random_index = 0

def logic_rule(row):
    # return random.randint(0, 2) == 0 # FIXME: this random value changed from python 2 to python 3, leading the test to fail
    global _py2_random_index
    random_randint_0_2_py2 = _random_randint_0_2_py2_stream[_py2_random_index]
    _py2_random_index += 1
    return random_randint_0_2_py2 == 0 # this replicates the random stream from python 2
