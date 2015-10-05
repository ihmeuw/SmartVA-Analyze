import functools
import re


class LdapNotationParser(object):
    def __init__(self, statement, arg1_fn=None, arg2_fn=None):
        """
        Parse and process LDAP search filter statement conditional arguments.
        Optional functions can be applied to either argument in the statement.
        Example usage:
        LdapNotationParser('(&(age>18)(sex=1))', lookup_fn, int)

        :param statement: String in LDAP search statement.
        :param arg1_fn: Function to apply to argument 1.
        :param arg2_fn: Function to apply to argument 2.
        """
        self.statement = statement
        self._arg1_fn = arg1_fn or LdapNotationParser.no_fn
        self._arg2_fn = arg2_fn or LdapNotationParser.no_fn

    def parse_element(self, element):
        arg1, cond, arg2 = re.match('(\w+)([<>=]+)(\w+)', element).groups()
        fn1 = self._arg1_fn(arg1)
        fn2 = self._arg2_fn(arg2)
        return LdapNotationParser.get_op(cond)(fn1, fn2)

    def _do_parse(self, parse_str):
        if parse_str[0] in ['(']:
            return [self._do_parse(group) for group in find_groups(parse_str)]
        elif parse_str[0] in ['!']:
            op = LdapNotationParser.get_op(parse_str[0])
            return op(self._do_parse(parse_str[1:])[0])
        elif parse_str[0] in ['&', '|']:
            op = LdapNotationParser.get_op(parse_str[0])
            return functools.reduce(op, self._do_parse(parse_str[1:]))
        else:
            return self.parse_element(parse_str)

    def _parse(self, parse_str):
        return self._do_parse(parse_str)[0]

    def parse(self):
        """
        Parse the statement and return a boolean value.

        :return: Boolean representation of parsed statement.
        """
        return self._parse(self.statement)

    @staticmethod
    def no_fn(arg):
        return arg

    @staticmethod
    def eq(arg1, arg2):
        return arg1 == arg2

    @staticmethod
    def gt(arg1, arg2):
        return arg1 > arg2

    @staticmethod
    def lt(arg1, arg2):
        return arg1 < arg2

    @staticmethod
    def ge(arg1, arg2):
        return arg1 >= arg2

    @staticmethod
    def le(arg1, arg2):
        return arg1 <= arg2

    @staticmethod
    def or_(*args):
        result = False
        for arg in args:
            if isinstance(arg, (list, tuple)):
                result |= LdapNotationParser.or_(*arg)
            else:
                result |= arg
        return result

    @staticmethod
    def and_(*args):
        result = True
        for arg in args:
            if isinstance(arg, (list, tuple)):
                result &= LdapNotationParser.and_(*arg)
            else:
                result &= arg
        return result

    @staticmethod
    def not_(arg):
        return not arg

    @classmethod
    def get_op(cls, op):
        return {
            '=': cls.eq,
            '>': cls.gt,
            '<': cls.lt,
            '>=': cls.ge,
            '=>': cls.ge,
            '<=': cls.le,
            '=<': cls.le,
            '!': cls.not_,
            '|': cls.or_,
            '&': cls.and_
        }.get(op)


def find_next_group(group_str, style='()'):
    """
    Return the next group of data contained in a specified style pair from a string.
    Example:
    find_next_group('(a=1)(b=2)') returns 'a=1'

    :param group_str: Any string to search for a group.
    :param style: Start and end characters of a group. Default='()'
    :return: First group found in the group string.
    """
    cnt = 0
    for i, c in enumerate(group_str):
        if c == style[0]:
            cnt += 1
        elif c == style[1]:
            cnt -= 1
        if cnt == 0:
            return group_str[1:i]
    return None


def find_groups(group_str, style='()'):
    """
    Return a list of group data contained in a specified style pair from a string.
    Example:
    find_groups('(a=1)((b=2)(c=3))') returns ['a=1', '(b=2)(c=3)']

    :param group_str: Any string to search for groups.
    :param style: Start and end characters of a group. Default='()'
    :return: List of groups found in the group string.
    """
    groups = []
    temp = group_str
    while len(temp):
        group = find_next_group(temp, style)
        if not group:
            return []
        groups.append(group)
        temp = temp[len(group) + 2:]
    return groups
