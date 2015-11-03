from smartva.adult_pre_symptom_prep import AdultPreSymptomPrep


class TestAdultPreSymptomPrep(object):
    def test_rename_odk_headers(self):
        headers = ['test1', 'test2', 'test3']

        conversion_map = {
            'test1': 't1_01',
            'test2': 't1_02',
        }

        AdultPreSymptomPrep.rename_odk_headers(headers, conversion_map)

        assert headers == ['t1_01', 't1_02', 'test3']

    def test_get_drop_index_list(self):
        headers = ['pre_test1', 'test1', 'test2', 'test3', 'post_test1']

        drop_index_list = AdultPreSymptomPrep.get_drop_index_list(headers, 'test')

        assert drop_index_list == [1, 2, 3]

    def test_drop_from_list(self):
        headers = ['pre_test1', 'test1', 'test2', 'test3', 'post_test1']
        drop_index_list = [1, 2, 3]

        headers = AdultPreSymptomPrep.drop_from_list(headers, drop_index_list)

        assert headers == ['pre_test1', 'post_test1']

    def test_verify_answers_for_row(self):
        headers = ['sid', 'test1', 'test2', 'test3']
        row = ['0', 1, 2, 2015]

        valid_range_data = {
            'test1': range(12 + 1),
            'test2': [1, 2, 3, 4, 5, 9],
            'test3': range(1900, 2016) + [9999]
        }

        warnings = AdultPreSymptomPrep.verify_answers_for_row(headers, row, valid_range_data)

        assert warnings is False

        # TODO - Break this out into own test and test warning logger.
        valid_range_data['test1'] = [0]

        warnings = AdultPreSymptomPrep.verify_answers_for_row(headers, row, valid_range_data)

        assert warnings is True

    def test_convert_free_text_words(self):
        headers = ['sid', 'test1', 'test2', 'test3']
        row = ['0', 0, 0, 0]

        word_list = ['pencil', 'eraser', 'watermelon']

        word_map = {
            # stem words
            'pencil': 'test1',
            'eras': 'test3',
            'watermelon': 'test4'
        }

        AdultPreSymptomPrep.convert_free_text_words(headers, row, word_list, word_map)

        assert row == ['0', 1, 0, 1]

    def test_convert_free_text_headers(self):
        headers = ['sid', 'test_words', 'test1', 'test2', 'test3']
        row = ['0', 'pencil eraser watermelon', 0, 0, 0]

        data_headers = ['test_words']

        word_map = {
            # stem words
            'pencil': 'test1',
            'eras': 'test3',
            'watermelon': 'test4'
        }

        AdultPreSymptomPrep.convert_free_text_headers(headers, row, data_headers, word_map)

        assert row == ['0', 'pencil eraser watermelon', 1, 0, 1]

    def test_consolidate_answers(self):
        headers = ['sid', 'test_a', 'test_b', 'test1', 'test2', 'test3']
        row = ['0', 13, 0, 1, 2, 3]

        consolidation_map = {
            ('test_a', 'test_b'): {
                11: 'test1',
                12: 'test2',
                13: 'test3',
            }
        }

        AdultPreSymptomPrep.consolidate_answers(headers, row, consolidation_map)

        assert row == ['0', 13, 3, 1, 2, 3]

    def test_fill_missing_data(self):
        headers = ['sid', 'test1', 'test2', 'test3', 'test4']
        row = ['0', '', '', 3, 4]

        default_fill = {
            'test1': 1,
            'test2': 9,
            'test3': 0
        }

        AdultPreSymptomPrep.fill_missing_data(headers, row, default_fill)

        assert row == ['0', 1, 9, 3, 4]

    def test_calculate_duration_variables(self):
        headers = ['sid', 'test1', 'test1a', 'test1b', 'test2', 'test2a', 'test2b']
        row = ['0', '', 1, 1, '', '', '']

        duration_vars = ['test1', 'test2']
        special_case_vars = {
            'test2': 999
        }

        AdultPreSymptomPrep.calculate_duration_variables(headers, row, duration_vars, special_case_vars)

        assert row == ['0', 356.0, 1, 1, 999, '', '']
