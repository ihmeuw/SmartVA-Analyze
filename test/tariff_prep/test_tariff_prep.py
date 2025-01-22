from collections import defaultdict, OrderedDict
import csv
import os

import pytest
import pandas as pd
import numpy as np

from smartva.tariff_prep import (
    Record,
    TariffPrep,
    get_tariff_matrix,
    clean_tariffs,
)

import sample_tariff_data
from smartva.tariff_prep import TariffPrep
from smartva.data import (
    adult_tariff_data,
    child_tariff_data,
    neonate_tariff_data,
)

module_data = [adult_tariff_data, child_tariff_data, neonate_tariff_data]


@pytest.fixture
def prep():
    return TariffPrep(sample_tariff_data, '/', True,
                      {'hce': True, 'free_text': True, 'hiv': True,
                       'malaria': True, 'chinese': False},
                      'USA', who_2016=True)


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
    with f_path.open('w') as f:
        w = csv.writer(f)
        w.writerows(input_data)

    result = get_tariff_matrix(f_path.strpath, ['xs_name'], {}, 5)

    print(result)

    for key in result:
        assert result[key] == expected_result[key]


@pytest.mark.parametrize('row,expected', [
    ({'sid': 'none', 'restricted': ''}, set()),
    ({'sid': 'one', 'restricted': '1'}, {1}),
    ({'sid': 'two', 'restricted': '1 2'}, {1, 2}),
])
def test_score_symptom_data_restricted(prep, row, expected):
    va = prep.score_symptom_data([row], {})[0]
    assert va.censored == expected


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
    train_data = [Record(scores={1: s}) for s in train_scores]
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
    test_data = [Record(scores={1: score}) for score, rank in tests]

    # Modifies list of Records in place and doesn't return anything
    prep.generate_cause_rankings(test_data, uniform_scores)

    predicted_test_ranks = [va.ranks[1] for va in test_data]
    actual_test_ranks = [float(rank) for score, rank in tests]
    assert predicted_test_ranks == actual_test_ranks


@pytest.mark.parametrize('censored,scores,ranks,expected', [
    ([], {1: 10}, {1: 7}, {1: 7}),
    ([1], {1: 10}, {1: 7}, {1: 9999}),
    ([1], {1: 10, 2: 10}, {1: 7, 2: 5}, {1: 9999, 2: 5}),
    ([1, 2], {1: 10, 2: 10}, {1: 7, 2: 5}, {1: 9999, 2: 9999}),
])
def test_mask_ranks(prep, censored, scores, ranks, expected):
    prep.cause_list = list(scores.keys())

    va = Record(scores=scores, censored=censored)
    va.ranks = ranks

    uniform = list(range(1000))  # just needs length
    cutoffs = dict(list(zip(list(scores.keys()), [99999] * len(scores))))
    demog_restrictions = {}
    lowest_rank = 9999   # value set if restricted
    uniform_list_pos = 999
    min_cause_score = defaultdict(lambda: 0)

    prep.mask_ranks([va], uniform, cutoffs, demog_restrictions, lowest_rank,
                    uniform_list_pos, min_cause_score)

    assert va.ranks == expected


@pytest.mark.parametrize('va, cause, cause_name', [
    (Record(sid='rules', cause=1), 11, 'c11'),
    (Record(sid='rules2', cause=2), 12, 'c12'),
    (Record(sid='ranks', ranks={1: 1, 2: 2}), 11, 'c11'),
    (Record(sid='rules_bad', cause='x', ranks={1: 1, 2: 2}), 11, 'c11'),
    (Record(sid='tie', ranks={1: 1, 2: 1, 3: 2}), 11, 'c11'),
    (Record(sid='lowest', ranks={1: 999, 2: 999, 3: 999}), None,
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

    user_data = [Record('sid{}'.format(i), age=35, sex=i % 2 + 1, cause=cause)
                 for i, cause in enumerate(causes) for i in range(counts[i])]

    csmf, csmf_by_sex = prep.calculate_csmf(user_data, [])

    assert np.allclose(sum(csmf.values()), 1)
    for sex, csmf_data in list(csmf_by_sex.items()):
        assert np.allclose(sum(csmf_data.values()), 1)


@pytest.mark.parametrize('tariff_data', module_data)
def test_training_likelihood_ranges(tariff_data):
    prep = TariffPrep(tariff_data, '/', True, {'hce': True, 'free_text': True, 'hiv': True, 'malaria': True, 'chinese': False}, 'USA', who_2016=True)
    drop_headers = {'xs_name'}
    drop_headers.update(prep.data_module.SHORT_FORM_DROP_LIST)
    tariffs = get_tariff_matrix(prep.tariffs_filename, drop_headers,
                                prep.data_module.SPURIOUS_ASSOCIATIONS)
    prep.cause_list = sorted(tariffs.keys())
    validated = prep.read_input_file(prep.validated_filename)[1]
    train = prep.process_training_data(validated, tariffs,
                                       prep.data_module.FREQUENCIES,
                                       prep.data_module.CUTOFF_POS,
                                       [.25, .5, .75])
    uniform_train = train[0]
    likelihoods = train[4]

    assert list(likelihoods.keys()) == prep.cause_list
    assert len(set(map(len, list(likelihoods.values())))) == 1
    for cause, likelihood in list(likelihoods.items()):
        assert likelihood[-1] == len(uniform_train)
        assert sorted(likelihood) == likelihood


@pytest.mark.parametrize('va, expected', [
    (Record(sid='no-prediction', ranks={1: 5}), []),
    (Record(sid='best-likelihood', cause=1, ranks={1: 5}), [(1, 0)]),
    (Record(sid='mid-likelihood', cause=1, ranks={1: 15}), [(1, 1)]),
    (Record(sid='low-likelihood', cause=1, ranks={1: 55}), [(1, 2)]),
    (Record(sid='negative-rank', cause=1, ranks={1: -5}), [(1, 0)]),
    (Record(sid='zero-rank', cause=1, ranks={1: 0}), [(1, 0)]),
    (Record(sid='at-threshold1', cause=1, ranks={1: 10}), [(1, 1)]),
    (Record(sid='at-threshold2', cause=1, ranks={1: 50}), [(1, 2)]),
    (Record(sid='at-highest-threshold', cause=1, ranks={1: 100}), [(1, 2)]),
    (Record(sid='above-highest-threshold', cause=1, ranks={1: 110}), [(1, 2)]),
    (Record(sid='rule-best-ranked', cause=1, rules=1, ranks={1: 5, 2: 10}),
        [(1, 0), (2, 0)]),
    (Record(sid='rule-best-ranked2', cause=1, rules=1, ranks={1: 5, 2: 90}),
        [(1, 0), (2, 2)]),
    (Record(sid='rule2-best-ranked', cause=2, rules=2, ranks={1: 5, 2: 10}),
        [(2, 0), (1, 0)]),
    (Record(sid='rule2-best-ranked2', cause=2, rules=2, ranks={1: 55, 2: 90}),
        [(2, 0), (1, 2)]),
    (Record(sid='rule-not-best-ranked', cause=1, rules=1,
            ranks={1: 40, 2: 10}), [(1, 0), (2, 0)]),
    (Record(sid='rule-not-best-ranked2', cause=1, rules=1,
            ranks={1: 40, 2: 90}), [(1, 0), (2, 2)]),
    (Record(sid='rule2-not-best-ranked', cause=2, rules=2,
            ranks={1: 5, 2: 10}), [(2, 0), (1, 0)]),
    (Record(sid='rule2-not-best-ranked2', cause=2, rules=2,
            ranks={1: 55, 2: 90}), [(2, 0), (1, 2)]),
    (Record(sid='rank-order', cause=1, ranks={1: 9, 2: 25, 3: 55}),
        [(1, 0), (2, 0), (3, 0)]),
    (Record(sid='rank-order2', cause=2, ranks={1: 9, 2: 5, 3: 7}),
        [(2, 0), (3, 0), (1, 0)]),
    (Record(sid='rank-order3', cause=2, ranks={1: 90, 2: 85, 3: 87}),
        [(2, 2), (3, 2), (1, 2)]),
    (Record(sid='capped1', cause=1, ranks={1: 55, 2: 56, 3: 57}),
        [(1, 2), (2, 2), (3, 2)]),
    (Record(sid='capped2', cause=1, ranks={1: 55, 2: 58, 3: 57}),
        [(1, 2), (3, 2), (2, 2)]),
    (Record(sid='capped-by-second', cause=2, ranks={1: 55, 2: 20, 3: 75}),
        [(2, 0), (1, 2), (3, 2)]),
    (Record(sid='aggregates', cause=5, ranks={5: 20}), [(4, 0)]),
    (Record(sid='aggregates-same', cause=5, ranks={4: 22, 5: 20}), [(4, 0)]),
    (Record(sid='aggregates-takes-best', cause=5, ranks={4: 55, 5: 20}),
        [(4, 0)]),
    (Record(sid='aggregates-takes-best-capped', cause=5, ranks={4: 50, 5: 30}),
        [(4, 1)]),
    (Record(sid='aggregates-takes-best-capped2', cause=5,
            ranks={3: 82, 4: 83, 5: 20}), [(4, 0), (3, 2)]),
])
def test_determine_likelihood(prep, va, expected):
    thresholds = {
        1: [0, 10, 50, 100],
        2: [0, 30, 60, 100],
        3: [0, 70, 80, 100],
        4: [0, 50, 85, 100],
        5: [0, 25, 60, 100],
    }
    cause_reduction = {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 4,
    }
    prep.determine_likelihood([va], thresholds, cause_reduction)
    assert va.likelihoods == OrderedDict(expected)
