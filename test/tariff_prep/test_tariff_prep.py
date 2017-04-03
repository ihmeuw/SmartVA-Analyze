from collections import defaultdict
import csv
import pytest

from smartva.tariff_prep import (
    ScoredVA,
    TariffPrep,
    get_cause_num,
    get_cause_symptoms,
)

import sample_tariff_data


class TariffPrepMock(TariffPrep):
    def _calc_age_bin(self, va, u_row):
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


def test_get_cause_num():
    assert get_cause_num('cause0') == 0


@pytest.mark.parametrize('row,expected', [
    ({'sid': 'none', 'restricted': ''}, []),
    ({'sid': 'one', 'restricted': '1'}, [1]),
    ({'sid': 'two', 'restricted': '1 2'}, [1, 2]),
], ids=lambda x: x['sid'])
def test_get_va_cause_list_restricted(tmpdir, prep, row, expected):
    f = tmpdir.join('test.csv')
    f.write('\n'.join([','.join(r) for r in zip(*row.items())]))
    va = prep.get_va_cause_list(f.strpath, {})[0]

    assert va.restricted == expected


def test_get_cause_symptoms(tmpdir):
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

    result = get_cause_symptoms(f_path.strpath, ['xs_name'], 5)

    print(result)

    for key in result:
        assert result[key] == expected_result[key]


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
    prep.generate_cause_rankings(test_data, train_data)

    predicted_test_ranks = [va.rank_list[1] for va in test_data]
    actual_test_ranks = [float(rank) for score, rank in tests]
    assert predicted_test_ranks == actual_test_ranks


@pytest.mark.parametrize('restrictions,scores,ranks,expected', [
    ([], {1: 10}, {1: 7}, {1: 7}),
    ([1], {1: 10}, {1: 7}, {1: 9999}),
    ([1], {1: 10, 2: 10}, {1: 7, 2: 5}, {1: 9999, 2: 5}),
    ([1, 2], {1: 10, 2: 10}, {1: 7, 2: 5}, {1: 9999, 2: 9999}),
])
def test_identify_lowest_ranked_cause_restricted(prep, restrictions, scores,
                                                 ranks, expected):
    prep.cause_list = scores.keys()

    va = ScoredVA(scores, 0, 'sid', 7, 2, restrictions)
    va.rank_list = ranks

    uniform = range(1000)  # just needs length
    cutoffs = dict(zip(scores.keys(), [99999] * len(scores)))
    demog_restrictions = {}
    lowest_rank = 9999   # value set if restricted
    uniform_list_pos = 999
    min_cause_score = defaultdict(lambda: 0)

    prep.identify_lowest_ranked_causes([va], uniform, cutoffs,
                                       demog_restrictions, lowest_rank,
                                       uniform_list_pos, min_cause_score)

    assert va.rank_list == expected
