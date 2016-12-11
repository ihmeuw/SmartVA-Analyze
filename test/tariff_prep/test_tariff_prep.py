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
    def _matches_undetermined_cause(self, va, u_row):
        return True


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

    train_scores = [100, 50, 10, 10, -3]
    train_data = [ScoredVA({1: s}, 0, 'sid', 7, 2) for s in train_scores]

    # Score, Rank within training
    tests = [
        (110, 1),  # above highest score in train data
        (100, 1),  # at highest score in train data
        (90, 1.5),
        (50, 2),   # at a value which exists in the train data
        (11, 2.5),
        (10, 3.5), # at a non-unique value in the train data
        (0, 4.5),  # zero (just in case)
        (-1, 4.5), # negative value in range of train scores max to min
        (-3, 5),   # at lowest score in train data
        (-5, 5),   # below lowest score in train data
    ]
    test_data = [ScoredVA({1: score}, 0, 'sid', 7, 2) for score, rank in tests]

    # Modifies list of ScoredVAs in place and doesn't return anything
    prep.generate_cause_rankings(test_data, train_data)

    predicted_test_ranks = [va.rank_list[1] for va in test_data]
    actual_test_ranks = [float(rank) for score, rank in tests]
    assert predicted_test_ranks == actual_test_ranks
