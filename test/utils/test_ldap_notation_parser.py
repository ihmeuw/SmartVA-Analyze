from smartva.utils import LdapNotationParser


def word_to_digit(word):
    return {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'zero': 0
    }.get(word.lower())


class TestLdapNotationParser(object):
    def test_true_conditions(self):
        test_args = [
            ['(1=1)', int, int],
            ['(&(one=1)(two=2))', word_to_digit, int],
            ['(|(three>2)(three=2))', word_to_digit, int],
            ['(&(!(four=5))(|(six=6)(seven=6)))', word_to_digit, int],
            ['(&(1>=1)(2>=1))', int, int],
            ['(&(1<=1)(0<=1))', int, int]
        ]
        for test_arg in test_args:
            assert LdapNotationParser(*test_arg).evaluate() is True

    def test_false_conditions(self):
        test_args = [
            ['(2=1)', int, int],
            ['(&(one=2)(two=2))', word_to_digit, int],
            ['(|(three<2)(three=2))', word_to_digit, int],
            ['(&(!(four=4))(|(six=6)(seven=6)))', word_to_digit, int],
            ['(&(1>=1)(2<=1))', int, int],
            ['(&(1<=1)(0>=1))', int, int]
        ]
        for test_arg in test_args:
            assert LdapNotationParser(*test_arg).evaluate() is False
