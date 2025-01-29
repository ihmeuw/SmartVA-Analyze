from argparse import Namespace

import pytest

from smartva.pre_symptom_prep import PreSymptomPrep


@pytest.fixture
def prep():
    data_module = Namespace(AGE_GROUP='test', DEFAULT_FILL={},
                            DEFAULT_FILL_SHORT={})
    return PreSymptomPrep(data_module, '', True, who_2016=True)


class TestPreSymptomPrep(object):
    def test_rename_odk_headers(self, prep):
        headers = ['test1', 'test2', 'test3']

        conversion_map = {
            'test1': 't1_01',
            'test2': 't1_02',
        }

        prep.rename_headers(headers, conversion_map)

        assert headers == ['t1_01', 't1_02', 'test3']

    def test_drop_from_list(self, prep):
        headers = ['pre_test1', 'test1', 'test2', 'test3', 'post_test1']
        drop_index_list = [1, 2, 3]

        headers = prep.drop_from_list(headers, drop_index_list)

        assert headers == ['pre_test1', 'post_test1']

    def test_verify_answers_for_row(self, prep):
        headers = ['sid', 'test1', 'test2', 'test3']
        row = dict(list(zip(headers, ['0', 1, 2, 2015])))

        valid_range_data = {
            'test1': list(range(12 + 1)),
            'test2': [1, 2, 3, 4, 5, 9],
            'test3': list(range(1900, 2016)) + [9999]
        }

        prep.verify_answers_for_row(row, valid_range_data)

        # TODO - Break this out into own test and test warning logger.
        valid_range_data['test1'] = [0]

        prep.verify_answers_for_row(row, valid_range_data)

    def test_convert_free_text_words(self, prep):
        headers = ['sid', 'test1', 'test2', 'test3']
        row = dict(list(zip(headers, ['0', 0, 0, 0])))

        word_list = ['pencil', 'eraser', 'watermelon']

        word_map = {
            # stem words
            'pencil': 'test1',
            'eras': 'test3',
            'watermelon': 'test4'
        }

        prep.convert_free_text_words(row, word_list, word_map)

        assert row == dict(list(zip(headers + ['test4'], ['0', 1, 0, 1, 1])))

    def test_convert_free_text_headers(self, prep):
        headers = ['sid', 'test_words', 'test1', 'test2', 'test3']
        row = dict(list(zip(headers, ['0', 'pencil eraser watermelon', 0, 0, 0])))

        data_headers = ['test_words']

        word_map = {
            # stem words
            'pencil': 'test1',
            'eras': 'test3',
            'watermelon': 'test4'
        }

        prep.convert_free_text_vars(row, data_headers, word_map)

        assert row == dict(list(zip(headers + ['test4'], ['0', 'pencil eraser watermelon', 1, 0, 1, 1])))

    def test_consolidate_answers(self, prep):
        headers = ['sid', 'test_a', 'test_b', 'test1', 'test2', 'test3']
        row = dict(list(zip(headers, ['0', 13, 0, 1, 2, 3])))

        consolidation_map = {
            ('test_a', 'test_b'): {
                11: 'test1',
                12: 'test2',
                13: 'test3',
            }
        }

        prep.recode_answers(row, consolidation_map)

        assert row == dict(list(zip(headers, ['0', 13, 3, 1, 2, 3])))

        # There's no guarentee that the columns that appear in the values
        # of the consolidation map actually appear in the data. If they are
        # missing the row should be filled with None
        row2 = dict(list(zip(headers[:-1], ['0', 13, 0, 1, 2])))
        prep.recode_answers(row2, consolidation_map)

        assert row2 == dict(list(zip(headers[:-1], ['0', 13, None, 1, 2])))

    def test_fill_missing_data(self, prep):
        headers = ['sid', 'test1', 'test2', 'test3', 'test4']
        row = dict(list(zip(headers, ['0', '', '', 3, 4])))

        default_fill = {
            'test1': 1,
            'test2': 9,
            'test3': 0
        }

        prep.fill_missing_data(row, default_fill)

        assert row == dict(list(zip(headers, ['0', 1, 9, 3, 4])))

    def test_calculate_duration_variables(self, prep):
        headers = ['sid', 'test1', 'test1a', 'test1b', 'test2', 'test2a', 'test2b', 'test3', 'test3a', 'test3b']
        row = dict(list(zip(headers, ['0', '', 1, 1, '', '', '', '', 2, 4])))

        duration_vars = ['test1', 'test2', 'test3']
        special_case_vars = {
            'test2': 999
        }

        prep.calculate_duration_vars(row, duration_vars, special_case_vars)

        assert row == dict(list(zip(headers, ['0', 365.0, 1, 1, 999, '', '', 120.0, 2, 4])))

    def test_process_age_vars(self, prep):

        # AGE_VARS = ['g5_04'] means year, months, days in g5_04a,b,c
        # are converted to float values of age in years, months, and days

        row = dict(sid='test', g5_04a='1', g5_04b='', g5_04c='')
        prep.process_age_vars(row)
        assert row['g5_04a'] == 1
        assert row['g5_04b'] == 12
        assert row['g5_04c'] == 365

        row = dict(sid='test', g5_04a='1', g5_04b='6', g5_04c='')
        prep.process_age_vars(row)
        assert row['g5_04a'] == 1.5
        assert row['g5_04b'] == 18.
        assert row['g5_04c'] <= 365 + 365/2.

        row = dict(sid='test', g5_04a='', g5_04b='', g5_04c='364')
        prep.process_age_vars(row)
        assert row['g5_04a'] < 1.
        assert row['g5_04b'] < 13.  # FIXME: a little funny to get months wrong-ish
        assert row['g5_04c'] == 364

        row = dict(sid='test', g5_04a='1', g5_04b='.', g5_04c='')
        prep.process_age_vars(row)
        assert row['g5_04a'] == 1.
        assert row['g5_04b'] == 12.
        assert row['g5_04c'] == 365.

    @pytest.mark.parametrize('row,endorsed', [
        ({'g5_01y': 2015, 'g5_01m': 1, 'g5_01d': 1, 'g5_02': 1, 'symp': 0,
          'date1y': 2015, 'date1m': 1, 'date1d': 15, 'weight1b': 700}, 1),
        ({'g5_01y': 2015, 'g5_01m': 1, 'g5_01d': 1, 'g5_02': 1, 'symp': 0,
          'date1y': 2015, 'date1m': 1, 'date1d': 15, 'weight1b': 7000}, 0),
        ({'symp': 0}, 0),
    ])
    def test_process_weight_sd_vars(self, prep, row, endorsed):
        exam_date_vars = {
            'date1': 'weight1',
            'date2': 'weight2',
        }
        weight_sd_data = {
            'symp': {
                1: {0: 2.5},
                2: {0: 2.5},
            }
        }
        prep.process_weight_sd_vars(row, exam_date_vars, weight_sd_data)

        assert row['symp'] == endorsed
