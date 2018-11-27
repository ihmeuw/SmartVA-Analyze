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

    @pytest.mark.parametrize('values, expected', [
        ('', ['', 0, 0, 0, 0, 0]),
        ('1', ['1', 1, 0, 0, 0, 0]),
        ('2', ['2', 0, 1, 0, 0, 0]),
        ('3', ['3', 0, 0, 1, 0, 0]),
        ('8', ['8', 0, 0, 0, 1, 0]),
        ('9', ['9', 0, 0, 0, 0, 1]),
        ('7', ['', 0, 0, 0, 0, 0]),  # out of range value
        ('1 2', ['1 2', 1, 1, 0, 0, 0]),
        ('1 2 8', ['1 2 8', 1, 1, 0, 1, 0]),
        ('1 X', ['', 0, 0, 0, 0, 0]),  # invalid value
        ('1.0', ['', 0, 0, 0, 0, 0]),  # must be ints
        ('1 2.0', ['', 0, 0, 0, 0, 0]),  # must be ints
    ])
    def test_process_multiselect_varss(self, prep, values, expected):
        row = {'input_header': values}
        conversion_data = {
            1: 'output1',
            2: 'output2',
            3: 'output3',
            8: 'output4',
            9: 'output5',
        }
        headers = ['input_header']
        headers.extend(sorted(conversion_data.values()))

        prep.process_multiselect_vars(row, 'input_header', conversion_data)
        assert row == dict(zip(headers, expected))

    @pytest.mark.parametrize('values, expected', [
        (['1 2 3', 0, 0, 0], ['1 2 3', 4, 0, 0]),
        (['1 2 4 5', 0, 0, 0], ['1 2 4 5', 4, 0, 0]),
        (['1 3', 0, 0, 0], ['1 3', 1, 3, 0]),
        (['', 0, 0, 0], ['', 0, 0, 0]),
        (['X', 0, 0, 0], ['X', 0, 0, 0]),
        (['1 X', 0, 0, 0], ['1 X', 0, 0, 0]),
    ])
    def test_convert_rash_data(self, prep, values, expected):
        headers = ['test', 'test1', 'test2', 'test3']
        row = dict(zip(headers, values))

        conversion_data = {
            'test': {
                'vars': ['test1', 'test2', 'test3'],
                'locations': [1, 2, 3],
                'values': {1, 2, 3, 4, 5, 8, 9},
                'everywhere': 4
            }
        }

        prep.convert_rash_data(row, conversion_data)

        assert row == dict(zip(headers, expected))

    @pytest.mark.parametrize('values, expected', [
        ([1, '1000', ''], [1, 1000, '']),
        ([2, '', '1.5'], [1, 1500, '']),
        ([1, '', ''], [1, '', '']),
        ([2, '', ''], [1, '', '']),
        ([9, '', ''], [1, '', '']),
    ])
    def test_convert_weight_data_g(self, prep, values, expected):
        headers = ['test', 'test1', 'test2']
        row = dict(zip(headers, values))

        conversion_data = {
            'test': {
                1: 'test1',
                2: 'test2'
            }
        }

        prep.convert_weight_data(row, conversion_data)

        assert row == dict(zip(headers, expected))

    def test_convert_free_text(self, prep):
        headers = ['test1', 'test2']
        row = dict(zip(headers, ['pencil bite.', 'eraser 123 burn']))

        free_text_headers = headers

        prep.convert_free_text(row, free_text_headers, common_data.WORD_SUBS)

        assert row == dict(zip(headers, ['pencil bite', 'eraser fire']))

    def test_consent(self, prep):
        headers = ['sid', 'consent']
        row = dict(zip(headers, ['1', '1']))

        assert prep.check_consent(row, 'consent', 7) is True

    def test_consent_refusal(self, prep):
        headers = ['sid', 'consent']
        row = dict(zip(headers, ['1', '0']))

        assert prep.check_consent(row, 'consent', 7) is False

    def test_consent_empty(self, prep):
        headers = ['sid', 'consent']
        row = dict(zip(headers, ['1', '']))

        assert prep.check_consent(row, 'consent', 7) is True

    def test_consent_garbage(self, prep):
        garbage = ['blah', '1.0', '0.0']
        headers = ['sid', 'consent']
        for value in garbage:
            row = dict(zip(headers, ['1', value]))

            assert prep.check_consent(row, 'consent', 7) is False

    def test_consent_not_exist(self, prep):
        headers = ['sid']
        row = dict(zip(headers, ['1']))

        assert prep.check_consent(row, 'consent', 7) is True


@pytest.mark.parametrize('row,module', [
    (['adult-age', '75', '', '', ''], 'adult'),
    (['adult-12', '12', '', '', ''], 'adult'),
    (['adult-module', '', '', '', '3'], 'adult'),
    (['child-age', '7', '', '', ''], 'child'),
    (['child-months', '', '100', '', ''], 'child'),
    (['child-5-years', '5', '', '', ''], 'child'),
    (['child-11-years', '11', '', '', ''], 'child'),
    (['child-60-months', '', '60', '', ''], 'child'),
    (['child-30-days', '', '', '30', ''], 'child'),
    (['child-1-month', '', '1', '', ''], 'child'),
    (['child-module', '', '', '', '2'], 'child'),
    (['neonate-age', '', '', '15', ''], 'neonate'),
    (['neonate-module', '', '', '', '1'], 'neonate'),
    (['neonate-28-days', '', '', '28', ''], 'neonate'),
    (['neonate-1-days', '', '', '1', ''], 'neonate'),
    (['neonate-0-days', '', '', '0', ''], 'neonate'),
    (['neonate-module', '', '', '', '1'], 'neonate'),
    (['no-data', '', '', '', ''], 'invalid-age'),
    (['refused', '', '', '', '8'], 'invalid-age'),
    (['dont-know', '', '', '', '9'], 'invalid-age'),
    (['refused-with-adult-data', '70', '', '', '8'], 'adult'),
    (['dont-know-with-adult-data', '70', '', '', '9'], 'adult'),
    (['refused-with-child-data', '', '7', '', '8'], 'child'),
    (['dont-know-with-child-data', '', '7', '', '9'], 'child'),
    (['refused-with-neonate-data', '', '', '7', '8'], 'neonate'),
    (['dont-know-with-neonate-data', '', '', '7', '9'], 'neonate'),
], ids=lambda x: x['sid'])
def test_save_row(tmpdir, row, module):
    prep = common_prep.CommonPrep(tmpdir.strpath, True)

    headers = ['sid', 'gen_5_4a', 'gen_5_4b', 'gen_5_4c', 'gen_5_4d']
    lines = [','.join(headers)]
    lines.append(','.join(row))
    lines.append('')   # in case the file needs a blank line at the end
    tmpdir.mkdir('intermediate-files').join('cleanheaders.csv').write('\n'.join(lines))

    prep.run()

    sids = {module: [row['sid'] for row in prep._matrix_data[module]] 
            for module in prep._matrix_data}
    assert row[0] in sids[module]
