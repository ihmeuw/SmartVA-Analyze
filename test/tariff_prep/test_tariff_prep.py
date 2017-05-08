from collections import defaultdict
import csv
import os

import pytest
import pandas as pd
import numpy as np

from smartva.tariff_prep import (
    ScoredVA,
    TariffPrep,
    get_tariff_matrix,
    clean_tariffs,
)

import sample_tariff_data


class TariffPrepMock(TariffPrep):
    def _calc_age_bin(self, age):
        return int(age / 5) * 5 if age < 80 else 80


@pytest.fixture
def prep():
    prep = TariffPrepMock('/', True, {'hce': True, 'free_text': True, 'hiv': True, 'malaria': True}, 'USA')
    prep.data_module = sample_tariff_data
    return prep


class TestTariffPrep(object):
    def test_class_members(self, prep):
        assert prep.hce
        assert prep.free_text
        assert prep.hiv_region
        assert prep.malaria_region
        assert prep.iso3 == 'USA'

        assert prep.cause_list == []

        assert prep.data_module == sample_tariff_data

        assert prep.AGE_GROUP == 'sample'


@pytest.mark.parametrize('row, drop_headers, expected', [
    ({'bad': ''}, ['bad'], []),
    ({'bad': '', 'symp': '1'}, ['bad'], [('symp', 1)]),
    ({'bad': '', 'bad2': '', 'symp': '1'}, ['bad', 'bad2'], [('symp', 1)]),
])
def test_clean_tariffs_drop_headers(row, drop_headers, expected):
    cleaned = clean_tariffs(row, drop_headers=drop_headers)
    assert cleaned == expected


@pytest.mark.parametrize('row, spurious, expected', [
    ({'symp1': 1, 'symp2': 2}, [], [('symp2', 2), ('symp1', 1)]),
    ({'symp1': 1, 'symp2': 2}, ['symp1'], [('symp2', 2)]),
    ({'symp1': 1, 'symp2': 2}, ['symp2'], [('symp1', 1)]),
    ({'symp1': 1, 'symp2': 2}, ['symp1', 'symp2'], []),
])
def test_clean_tariffs_spurious(row, spurious, expected):
    cleaned = clean_tariffs(row, spurious=spurious)
    assert cleaned == expected


@pytest.mark.parametrize('row, max_symptoms, expected', [
    ({'symp1': 5, 'symp2': 4, 'symp3': 3}, 2, [('symp1', 5), ('symp2', 4)]),
    ({'symp1': 5, 'symp2': 4, 'symp3': 3}, 1, [('symp1', 5)]),
    ({'symp1': 5, 'symp2': 4, 'symp3': 3}, 0, []),
    ({'symp1': 5, 'symp2': -5, 'symp3': 3}, 2, [('symp1', 5), ('symp2', -5)]),
])
def test_clean_tariffs_max_symptoms(row, max_symptoms, expected):
    cleaned = clean_tariffs(row, max_symptoms=max_symptoms)
    assert cleaned == expected


@pytest.mark.parametrize('row, precision, expected', [
    ({'symp': '1.1'}, 0.5, [('symp', 1.0)]),
    ({'symp': '1.6'}, 0.5, [('symp', 1.5)]),
    ({'symp': '1.7499'}, 0.5, [('symp', 1.5)]),
    ({'symp': '1.75'}, 0.5, [('symp', 2.0)]),
])
def test_clean_tariffs_precision(row, precision, expected):
    cleaned = clean_tariffs(row, precision=precision)
    assert cleaned == expected


def test_get_tariff_matrix(tmpdir):
    input_data = [
        ['xs_name', 'age', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8'],
        ['cause1', '10.0', '8.0', '6.0', '4.0', '2.0', '0.0', '-1.0', '-3.0', '-5.0'],
        ['cause2', '8.0', '6.0', '4.0', '2.0', '0.0', '-1.0', '-3.0', '-5.0', '-7.0'],
        ['cause3', '6.0', '4.0', '2.0', '0.0', '-1.0', '-3.0', '-5.0', '-7.0', '-9.0'],
        ['cause4', '6.0', '4.0', '2.0', '0.0', '0.0', '0.0', '-5.0', '-1.0', '-3.0'],
        ['cause5', '4.0', '2.0', '0.0', '0.0', '0.0', '0.0', '0.0', '-1.0', '-3.0'],
        ['cause6', '4', '2', '0', '0', '0', '0', '0', '-1', '-3']  # must work with floats and ints
    ]

    expected_result = {
        1: [('age', 10.0), ('s1', 8.0), ('s2', 6.0), ('s8', -5.0), ('s3', 4.0)],
        2: [('age', 8.0), ('s8', -7.0), ('s1', 6.0), ('s7', -5.0), ('s2', 4.0)],
        3: [('s8', -9.0), ('s7', -7.0), ('age', 6.0), ('s6', -5.0), ('s1', 4.0)],
        4: [('age', 6.0), ('s6', -5.0), ('s1', 4.0), ('s8', -3.0), ('s2', 2.0)],
        5: [('age', 4.0), ('s8', -3.0), ('s1', 2.0), ('s7', -1.0)],
        6: [('age', 4.0), ('s8', -3.0), ('s1', 2.0), ('s7', -1.0)]
    }

    f_path = tmpdir.join('tariff-sample.csv')
    with f_path.open('wb') as f:
        w = csv.writer(f)
        w.writerows(input_data)

    result = get_tariff_matrix(f_path.strpath, ['xs_name'], {}, 5)

    print(result)

    for key in result:
        assert result[key] == expected_result[key]


@pytest.mark.parametrize('row,expected', [
    ({'sid': 'none', 'restricted': ''}, []),
    ({'sid': 'one', 'restricted': '1'}, [1]),
    ({'sid': 'two', 'restricted': '1 2'}, [1, 2]),
], ids=lambda x: x['sid'])
def test_score_symptom_data_restricted(prep, row, expected):
    va = prep.score_symptom_data([row], {})[0]
    assert va.restricted == expected


@pytest.mark.parametrize('row, key, expected', [
    ({'va46': '1.0'}, 'va46', 1),
    ({'cause': '1.0'}, 'cause', 1),
    ({'cause': '1.0'}, '', 0),
])
def test_score_symptom_data_cause_key(prep, row, key, expected):
    va = prep.score_symptom_data([row], {}, key)[0]
    assert va.cause == expected


@pytest.mark.parametrize('row, expected', [
    ({'symp1': 0, 'symp2': 0, 'symp3': 0, 'symp4': 0}, {1: 0, 2: 0, 3: 0}),
    ({'symp1': 1, 'symp2': 1, 'symp3': 1, 'symp4': 1}, {1: 4, 2: 5, 3: 7}),
    ({'symp1': 1, 'symp2': 0, 'symp3': 0, 'symp4': 0}, {1: 1, 2: 3, 3: 0}),
    ({'symp1': 0, 'symp2': 1, 'symp3': 0, 'symp4': 0}, {1: 1, 2: 0, 3: 7}),
    ({'symp1': 0, 'symp2': 0, 'symp3': 1, 'symp4': 0}, {1: 1, 2: 0, 3: 0}),
    ({'symp1': 0, 'symp2': 0, 'symp3': 0, 'symp4': 1}, {1: 1, 2: 2, 3: 0}),
])
def test_score_symptom_data_scoring(prep, row, expected):
    tariffs = {
        1: [('symp1', 1), ('symp2', 1), ('symp3', 1), ('symp4', 1)],
        2: [('symp1', 3), ('symp4', 2)],
        3: [('symp2', 7)],
    }

    scored = prep.score_symptom_data([row], tariffs)[0].scores
    assert scored == expected


def test_generate_cause_rankings(prep):
    prep.cause_list = [1]

    train_scores = [
        100,   # rank 1
        50,   # rank 2
        15,   # rank 3 (triplicate)
        15,   # rank 4 (triplicate)
        15,   # rank 5 (triplicate)
        10,   # rank 6 (duplicate positive)
        10,   # rank 7 (duplicate positive)
        -2,   # rank 8 (duplicate negative)
        -2,   # rank 9 (duplicate negative)
        -3,   # rank 10
    ]
    train_data = [ScoredVA({1: s}, 0, 'sid', 7, 2, []) for s in train_scores]
    uniform_scores = {1: np.sort([va.scores[1] for va in train_data])}

    # Score, Rank within training
    tests = [
        (110, 0.5),  # above highest score in train data
        (100, 1),  # at highest score in train data
        (90, 1.5),
        (50, 2),   # at a value which exists in the train data
        (15, 4),   # at triplicate value in the train data
        (11, 5.5),
        (10, 6.5), # at a duplicate value in the train data
        (0, 7.5),  # zero (just in case)
        (-1, 7.5), # negative value in range of train scores max to min
        (-3, 10),   # at lowest score in train data
        (-5, 10.5),   # below lowest score in train data
    ]
    test_data = [ScoredVA({1: score}, 0, 'sid', 7, 2, []) for score, rank in tests]

    # Modifies list of ScoredVAs in place and doesn't return anything
    prep.generate_cause_rankings(test_data, uniform_scores)

    predicted_test_ranks = [va.ranks[1] for va in test_data]
    actual_test_ranks = [float(rank) for score, rank in tests]
    assert predicted_test_ranks == actual_test_ranks


@pytest.mark.parametrize('restrictions,scores,ranks,expected', [
    ([], {1: 10}, {1: 7}, {1: 7}),
    ([1], {1: 10}, {1: 7}, {1: 9999}),
    ([1], {1: 10, 2: 10}, {1: 7, 2: 5}, {1: 9999, 2: 5}),
    ([1, 2], {1: 10, 2: 10}, {1: 7, 2: 5}, {1: 9999, 2: 9999}),
])
def test_mask_ranks(prep, restrictions, scores, ranks, expected):
    prep.cause_list = scores.keys()

    va = ScoredVA(scores, 0, 'sid', 7, 2, restrictions)
    va.ranks = ranks

    uniform = range(1000)  # just needs length
    cutoffs = dict(zip(scores.keys(), [99999] * len(scores)))
    demog_restrictions = {}
    lowest_rank = 9999   # value set if restricted
    uniform_list_pos = 999
    min_cause_score = defaultdict(lambda: 0)

    prep.mask_ranks([va], uniform, cutoffs, demog_restrictions, lowest_rank,
                    uniform_list_pos, min_cause_score)

    assert va.ranks == expected


@pytest.mark.parametrize('va, cause, cause_name', [
    (ScoredVA(sid='rules', cause=1), 11, 'c11'),
    (ScoredVA(sid='rules2', cause=2), 12, 'c12'),
    (ScoredVA(sid='ranks', ranks={1: 1, 2: 2}), 11, 'c11'),
    (ScoredVA(sid='rules_bad', cause='x', ranks={1: 1, 2: 2}), 11, 'c11'),
    (ScoredVA(sid='tie', ranks={1: 1, 2: 1, 3: 2}), 11, 'c11'),
    (ScoredVA(sid='lowest', ranks={1: 999, 2: 999, 3: 999}), None,
     'Undetermined'),
])
def test_predict_with_rule(prep, va, cause, cause_name):
    user_data = [va]
    cause_reduction = {1: 11, 2: 12, 3: 13, 4: 14}
    names34 = {11: 'c11', 12: 'c12', 13: 'c13', 14: 'c14'}
    names46 = {1: 'c1', 2: 'c2', 3: 'c3', 4: 'c4'}
    prep.predict(user_data, 999, cause_reduction, names34, names46)

    assert va.cause34 == cause
    assert va.cause34_name == cause_name


def test_csmf_summed_to_one(prep):
    causes = ['a', 'b', 'c']
    counts = np.random.randint(10, 100, 3)

    user_data = [ScoredVA({}, cause, '', 0, 1, '')
                 for i, cause in enumerate(causes) for _ in range(counts[i])]

    csmf = prep.calculate_csmf(user_data, [])

    assert np.allclose(sum(csmf.values()), 1)
