from collections import defaultdict, OrderedDict

import pytest

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


def test_get_age_key_12_19():
    assert cause_grapher.get_age_key(12) == '12-19 years'
    assert cause_grapher.get_age_key(19.9) == '12-19 years'


@pytest.mark.parametrize('age, label', [
    (0, '0-28 days'),
    (12. / 365, '0-28 days'),
    (28. / 365, '0-28 days'),
    (29. / 365, '29 days - 1 year'),
    (77. / 365, '29 days - 1 year'),
    (364. / 365, '29 days - 1 year'),
    (1, '1-4 years'),
    (3, '1-4 years'),
    (4.99999, '1-4 years'),
    (5, '5-11 years'),
    (7, '5-11 years'),
    (11.99999, '5-11 years'),
    (12, '12-19 years'),
    (17, '12-19 years'),
    (19.99999, '12-19 years'),
    (20, '20-29 years'),
    (27, '20-29 years'),
    (29.99999, '20-29 years'),
    (30, '30-39 years'),
    (37, '30-39 years'),
    (39.99999, '30-39 years'),
    (40, '40-49 years'),
    (47, '40-49 years'),
    (49.99999, '40-49 years'),
    (50, '50-59 years'),
    (57, '50-59 years'),
    (59.99999, '50-59 years'),
    (60, '60-69 years'),
    (67, '60-69 years'),
    (69.99999, '60-69 years'),
    (70, '70-79 years'),
    (77, '70-79 years'),
    (79.99999, '70-79 years'),
    (80, '80+ years'),
    (87, '80+ years'),
    (125, '80+ years'),
    (-1, 'Unknown'),
])
def test_get_age_key(age, label):
    assert cause_grapher.get_age_key(age) == label
