from smartva import common_prep
from smartva.data import common_data


class TestCommonPrep(object):
    def test_convert_cell_to_int(self):
        headers = ['test1', 'test2', 'test3']
        row = dict(zip(headers, ['0', '1', '']))

        common_prep.CommonPrep.convert_cell_to_int(row, headers)

        assert row == dict(zip(headers, [0, 1, 0]))

    def test_convert_binary_variables(self):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 3', 0, 0, 0]))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2',
                3: 'test3'
            }
        }

        common_prep.CommonPrep.process_binary_vars(row, conversion_data.items())

        assert row == dict(zip(headers, ['1 3', 1, 0, 1]))

    def test_convert_binary_variables_none(self):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['', 0, 0, 0]))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2',
                3: 'test3'
            }
        }

        common_prep.CommonPrep.process_binary_vars(row, conversion_data.items())

        assert row == dict(zip(headers, ['', 0, 0, 0]))

    def test_convert_rash_data_all(self):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 2 3', 0, 0, 0]))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': {
                    'one': 1,
                    'two': 2,
                    'three': 3
                },
                'everywhere': 4
            }
        }

        common_prep.CommonPrep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['1 2 3', 4, 0, 0]))

    def test_convert_rash_data_some(self):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['1 3', 0, 0, 0]))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': {
                    'one': 1,
                    'two': 2,
                    'three': 3
                },
                'everywhere': 4
            }
        }

        common_prep.CommonPrep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['1 3', 1, 3, 0]))

    def test_convert_rash_data_none(self):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, ['', 0, 0, 0]))

        conversion_data = {
            'test': {
                'headers': ['test1', 'test2', 'test3'],
                'list': [1, 2, 3],
                'value': 4
            }
        }

        common_prep.CommonPrep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, ['', 0, 0, 0]))

    def test_convert_weight_data_g(self):
        headers = ['test', 'test1', 'test2']
        row = dict(zip(headers, [1, '1000', '0']))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2'
            }
        }

        common_prep.CommonPrep.convert_weight_data(row, conversion_data)

        assert row == dict(zip(headers, [1, '1000', '0']))

    def test_convert_weight_data_kg(self):
        headers = ['test', 'test1', 'test2']
        row = dict(zip(headers, [2, 0, '1.5']))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2'
            }
        }

        common_prep.CommonPrep.convert_weight_data(row, conversion_data)

        assert row == dict(zip(headers, [1, 1500.0, '1.5']))

    def test_convert_free_text(self):
        headers = ['test1', 'test2']
        row = dict(zip(headers, ['pencil bite.', 'eraser 123 burn']))

        free_text_headers = headers

        common_prep.CommonPrep.convert_free_text(row, free_text_headers, common_data.WORD_SUBS)

        assert row == dict(zip(headers, ['pencil bite', 'eraser fire']))
