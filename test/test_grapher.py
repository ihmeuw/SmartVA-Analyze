from collections import defaultdict, OrderedDict

from smartva import cause_grapher
from smartva.data.common_data import MALE, FEMALE


def test_get_default_dict():
    valid_d = {
        'test': {
            MALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0),
            FEMALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0)
        }
    }

    d = defaultdict(cause_grapher.get_default_dict)
    d['test']  # Evoke the default dict.

    assert d == valid_d


def test_get_default_dict_inc():
    valid_d = {
        'test': {
            MALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0),
            FEMALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0)
        }
    }
    valid_d['test'][MALE]['0-28 days'] += 1

    d = defaultdict(cause_grapher.get_default_dict)
    d['test'][MALE]['0-28 days'] += 1

    assert d == valid_d


def test_get_age_key_0_28():
    assert cause_grapher.get_age_key(0) == '0-28 days'
    assert cause_grapher.get_age_key(28. / 365) == '0-28 days'


def test_get_age_key_29_1():
    assert cause_grapher.get_age_key(29. / 365) == '29 days - 1 year'
    assert cause_grapher.get_age_key(364. / 365) == '29 days - 1 year'


def test_get_age_key_1_4():
    assert cause_grapher.get_age_key(1) == '1-4 years'
    assert cause_grapher.get_age_key(4.9) == '1-4 years'


def test_get_age_key_5_11():
    assert cause_grapher.get_age_key(5) == '5-11 years'
    assert cause_grapher.get_age_key(11.9) == '5-11 years'


def test_get_age_key_12_19():
    assert cause_grapher.get_age_key(12) == '12-19 years'
    assert cause_grapher.get_age_key(19.9) == '12-19 years'


def test_get_age_key_20_44():
    assert cause_grapher.get_age_key(20) == '20-44 years'
    assert cause_grapher.get_age_key(44.9) == '20-44 years'


def test_get_age_key_45_59():
    assert cause_grapher.get_age_key(45) == '45-59 years'
    assert cause_grapher.get_age_key(59.9) == '45-59 years'


def test_get_age_key_60_plus():
    assert cause_grapher.get_age_key(60) == '60+ years'
    assert cause_grapher.get_age_key(100) == '60+ years'


def test_get_age_key_unknown():
    assert cause_grapher.get_age_key(-1) == 'Unknown'


