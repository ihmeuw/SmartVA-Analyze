import pytest

from smartva import common_prep
from smartva.data import common_data


@pytest.fixture
def prep():
    return common_prep.CommonPrep('', True)


class TestCommonPrep(object):
    def test_convert_cell_to_int(self, prep):
        headers = ['test1', 'test2', 'test3']
        row = dict(zip(headers, ['0', '1', '']))

        prep.convert_cell_to_int(row, headers)

        assert row == dict(zip(headers, [0, 1, 0]))

    def test_convert_binary_variables(self, prep):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 3', 0, 0, 0]))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2',
                3: 'test3'
            }
        }

        prep.process_binary_vars(row, conversion_data.items())

        assert row == dict(zip(headers, ['1 3', 1, 0, 1]))

    def test_convert_binary_variables_none(self, prep):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['', 0, 0, 0]))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2',
                3: 'test3'
            }
        }

        prep.process_binary_vars(row, conversion_data.items())

        assert row == dict(zip(headers, ['', 0, 0, 0]))

    def test_convert_rash_data_all(self, prep):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 2 3', 0, 0, 0]))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': [1, 2, 3],
                'everywhere': 4
            }
        }

        prep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['1 2 3', 4, 0, 0]))

    def test_convert_rash_data_all2(self, prep):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 2 4 5', 0, 0, 0]))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': [1, 2, 3],
                'everywhere': 4
            }
        }

        prep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['1 2 4 5', 4, 0, 0]))

    def test_convert_rash_data_some(self, prep):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 3', 0, 0, 0]))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': [1, 2, 3],
                'everywhere': 4
            }
        }

        prep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['1 3', 1, 3, 0]))

    def test_convert_rash_data_none(self, prep):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['', 0, 0, 0]))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': [1, 2, 3],
                'everywhere': 4
            }
        }

        prep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['', 0, 0, 0]))

    def test_convert_weight_data_g(self, prep):
        headers = ['test', 'test1', 'test2']
        row = dict(zip(headers, [1, '1000', '0']))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2'
            }
        }

        prep.convert_weight_data(row, conversion_data)

        assert row == dict(zip(headers, [1, '1000', '0']))

    def test_convert_weight_data_kg(self, prep):
        headers = ['test', 'test1', 'test2']
        row = dict(zip(headers, [2, 0, '1.5']))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2'
            }
        }

        prep.convert_weight_data(row, conversion_data)

        assert row == dict(zip(headers, [1, 1500.0, '1.5']))

    def test_convert_free_text(self, prep):
        headers = ['test1', 'test2']
        row = dict(zip(headers, ['pencil bite.', 'eraser 123 burn']))

        free_text_headers = headers

        prep.convert_free_text(row, free_text_headers, common_data.WORD_SUBS)

        assert row == dict(zip(headers, ['pencil bite', 'eraser fire']))

    def test_consent(self, prep):
        headers = ['sid', 'consent']
        row = dict(zip(headers, ['1', '1']))

        assert prep.check_consent(row, 'consent') is True

    def test_consent_refusal(self, prep):
        headers = ['sid', 'consent']
        row = dict(zip(headers, ['1', '0']))

        assert prep.check_consent(row, 'consent') is False

    def test_consent_empty(self, prep):
        headers = ['sid', 'consent']
        row = dict(zip(headers, ['1', '']))

        assert prep.check_consent(row, 'consent') is True

    def test_consent_garbage(self, prep):
        garbage = ['blah', '1.0', '0.0']
        headers = ['sid', 'consent']
        for value in garbage:
            row = dict(zip(headers, ['1', value]))

            assert prep.check_consent(row, 'consent') is False

    def test_consent_not_exist(self, prep):
        headers = ['sid']
        row = dict(zip(headers, ['1']))

        assert prep.check_consent(row, 'consent') is True
