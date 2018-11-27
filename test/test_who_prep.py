import pytest

from smartva.who_prep import WHOPrep


@pytest.fixture
def prep():
    return WHOPrep('/')


@pytest.mark.parametrize('row, expected', [
    ({'Id10013': 'yes'}, 1),
    ({'Id10013': 'no'}, 0),
    ({'Id10013': 'Yes'}, 0),
    ({'Id10013': 'YES'}, 0),
    ({'Id10013': '1'}, 0),
    ({'Id10013': True}, 0),
    ({'Id10013': 1}, 0),
    ({'Id10013': None}, 0),
    ({'Id10013': ''}, 0),
])
def test_determine_consent(prep, row, expected):
    prep.determine_consent(row)
    assert row['gen_3_1'] is expected


def test_determine_consent_does_not_fill_value(prep):
    row = {}
    prep.determine_consent(row)
    assert 'gen_3_1' not in row


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': '', 'dest_c': ''}),
    ({'src_a': 'yes', 'src_b': 'no', 'src_c': 'dk'},
     {'src_a': 'yes', 'src_b': 'no', 'src_c': 'dk', 'dest_a': 1, 'dest_b': 0,
      'dest_c': 9}),
    ({'xxx': 'foo', 'src_a': 'yes'},
     {'xxx': 'foo', 'src_a': 'yes', 'dest_a': 1, 'dest_b': '', 'dest_c': ''}),
    ({'xxx': 'foo', 'src_a': 1},
     {'xxx': 'foo', 'src_a': 1, 'dest_a': '', 'dest_b': '', 'dest_c': ''}),
    ({'xxx': 'foo', 'src_a': 'YES'},
     {'xxx': 'foo', 'src_a': 'YES', 'dest_a': '', 'dest_b': '', 'dest_c': ''}),
    ({'xxx': 'foo', 'src_a': None},
     {'xxx': 'foo', 'src_a': None, 'dest_a': '', 'dest_b': '', 'dest_c': ''}),
])
def test_recode_yes_no_questions(prep, row, expected):
    prep.data_module.YES_NO_QUESTIONS = {
        'dest_a': 'src_a',
        'dest_b': 'src_b',
        'dest_c': 'src_c',
    }
    prep.recode_yes_no_questions(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': ''}),
    ({'src_a': 'foo', 'src_b': '1'},
     {'src_a': 'foo', 'src_b': '1', 'dest_a': 1, 'dest_b': 3}),
    ({'src_a': 'bar', 'src_b': 'qux'},
     {'src_a': 'bar', 'src_b': 'qux', 'dest_a': 2, 'dest_b': 9}),
    ({'xxx': 'yyy', 'src_a': '', 'src_b':  None},
     {'xxx': 'yyy', 'src_a': '', 'src_b':  None, 'dest_a': '', 'dest_b': ''}),
    ({'xxx': 'yyy', 'src_a': 1, 'src_b':  9},
     {'xxx': 'yyy', 'src_a': 1, 'src_b':  9, 'dest_a': '', 'dest_b': ''}),
])
def test_recode_categoricals(prep, row, expected):
    prep.data_module.RECODE_QUESTIONS = {
        ('dest_a', 'src_a'): {'foo': 1, 'bar': 2},
        ('dest_b', 'src_b'): {'1': 3, 'qux': 9},
    }
    prep.recode_categoricals(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': '', 'dest_c': ''}),
    ({'xxx': 'foo', 'src_a': 'yes', 'src_b': 0, 'src_c': None},
     {'xxx': 'foo', 'src_a': 'yes', 'src_b': 0, 'src_c': None, 'dest_a': 'yes',
      'dest_b': 0, 'dest_c': None}),
])
def test_rename_questions(prep, row, expected):
    prep.data_module.RENAME_QUESTIONS = {
        'dest_a': 'src_a',
        'dest_b': 'src_b',
        'dest_c': 'src_c',
    }
    prep.rename_questions(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': ''}),
    ({'xxx': 'foo', 'src_a1': 'yes', 'src_a3': 'no', 'src_b1': 'no',
      'src_b2': 'yes', 'src_b3': 'yes'},
     {'xxx': 'foo', 'src_a1': 'yes', 'src_a3': 'no', 'src_b1': 'no',
      'src_b2': 'yes', 'src_b3': 'yes', 'dest_a': '1', 'dest_b': '7 12'})
])
def test_reverse_one_hot_multiselect(prep, row, expected):
    prep.data_module.REVERSE_ONE_HOT_MULTISELECT = {
        'dest_a': {'src_a1': 1, 'src_a2': 2, 'src_a3': 3},
        'dest_b': {'src_b1': 4, 'src_b2': 12, 'src_b3': 7},
    }
    prep.reverse_one_hot_multiselect(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': ''}),
    ({'xxx': 'foo', 'src_a': 'one two three', 'src_b': 'why ex'},
     {'xxx': 'foo', 'src_a': 'one two three', 'src_b': 'why ex',
      'dest_a': '1 2 3', 'dest_b': 'x y'}),
    ({'xxx': 'foo', 'src_a': 'one four three', 'src_b': 'z yes'},
     {'xxx': 'foo', 'src_a': 'one four three', 'src_b': 'z yes',
      'dest_a': '1 3', 'dest_b': '7'}),
])
def test_recode_multiselects(prep, row, expected):
    prep.data_module.RECODE_MULTISELECT = {
        ('dest_a', 'src_a'): {'one': 1, 'two': 2, 'three': 3},
        ('dest_b', 'src_b'): {'ex': 'x', 'why': 'y', 'z': 7}
    }
    prep.recode_multiselects(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': ''}),
    ({'xxx': 'qux', 'src_a': 'foo','src_b': 'bar'},
     {'xxx': 'qux', 'src_a': 'foo', 'src_b': 'bar', 'dest_a': 1, 'dest_b': 1}),
    ({'xxx': 'qux', 'src_a': 'things foo stuff', 'src_b': 'fa la la'},
     {'xxx': 'qux', 'src_a': 'things foo stuff', 'src_b': 'fa la la',
      'dest_a': 1, 'dest_b': 0}),
])
def test_encode_one_hot_from_multiselect(prep, row, expected):
    prep.data_module.ONE_HOT_FROM_MULTISELECT = {
        'dest_a': ('src_a', 'foo'),
        'dest_b': ('src_b', 'bar'),
    }
    prep.encode_one_hot_from_multiselect(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a': '', 'dest_b': ''}),
    ({'xxx': 'foo', 'src_a': 8, 'src_b': 0},
     {'xxx': 'foo', 'src_a': 8, 'src_b': 0, 'dest_a': 7, 'dest_b': ''}),
    ({'xxx': 'foo', 'src_a': None, 'src_b': 1},
     {'xxx': 'foo', 'src_a': None, 'src_b': 1, 'dest_a': '', 'dest_b': 3}),
])
def test_map_units_from_values(prep, row, expected):
    prep.data_module.UNIT_IF_AMOUNT = {
        'dest_a': ('src_a', 7),
        'dest_b': ('src_b', 3),
    }
    prep.map_units_from_values(row)
    assert row == expected


@pytest.mark.parametrize('row, expected', [
    ({}, {'dest_a_unit': '', 'dest_a_value': '', 'dest_b_unit': '',
          'dest_b_value': ''}),
    ({'xxx': 'foo', 'src_a1': 12, 'src_b1': 2},
     {'xxx': 'foo', 'src_a1': 12, 'src_b1': 2, 'dest_a_unit': 4,
      'dest_a_value': 12, 'dest_b_unit': 1, 'dest_b_value': 28})
])
def test_convert_durations(prep, row, expected):
    prep.data_module.DURATION_CONVERSIONS = {
        ('dest_a_unit', 'dest_a_value', 4): {'src_a1': 1, 'src_a2': 30},
        ('dest_b_unit', 'dest_b_value', 1): {'src_b1': 14, 'src_b2': 7},
    }
    prep.convert_durations(row)
    assert row == expected
