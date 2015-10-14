from smartva.adult_symptom_prep import AdultSymptomPrep


class TestAdultSymptomPrep(object):
    def test_copy_variables(self):
        headers = ['test1', 'test2', 'test3', 'test4']
        row = [2, 37, 0, 0]

        conversion_map = {
            'test1': 'test3',
            'test2': 'test4',
        }

        AdultSymptomPrep.copy_variables(headers, row, conversion_map)

        assert row == [2, 37, 2, 37]

    def test_process_quartile_data(self):
        headers = ['test0', 'test1', 'test2', 'test3', 'test4']
        rows = [
            [72, 0, 0, 0, 0],
            [12, 0, 0, 0, 0],
            [35, 0, 0, 0, 0],
            [48, 0, 0, 0, 0],
        ]

        valid_results = [
            [72, 0, 0, 0, 1],
            [12, 1, 0, 0, 0],
            [35, 0, 1, 0, 0],
            [48, 0, 0, 1, 0],
        ]

        conversion_map = {
            'test0': [
                (65, 'test4'),
                (45, 'test3'),
                (25, 'test2'),
                (0, 'test1')
            ]
        }

        for i, row in enumerate(rows):
            AdultSymptomPrep.process_quartile_data(headers, row, conversion_map.items())

            assert row == valid_results[i]

    def test_process_cutoff_data(self):
        headers = ['test1', 'test2', 'test3', 'test4']
        row = [0.12345, 40, 20, '']

        conversion_map = {
            'test1': 0.1234,
            'test2': 50,
            'test3': 10,
            'test4': 1
        }

        AdultSymptomPrep.process_cutoff_data(headers, row, conversion_map.items())

        assert row == [1, 0, 1, 0]

    def test_process_injury_data(self):
        headers = ['test0', 'test1', 'test2', 'test3', 'test4']
        rows = [
            [999, 1, 0, 1, 0],
            [40, 1, 0, 1, 0],
            [28, 1, 0, 1, 0]
        ]

        valid_results = [
            [999, 0, 0, 0, 0],
            [40, 0, 0, 0, 0],
            [28, 1, 0, 1, 0]
        ]

        conversion_map = {
            'test0': ['test1', 'test2', 'test3', 'test4']
        }

        for i, row in enumerate(rows):
            AdultSymptomPrep.process_injury_data(headers, row, conversion_map.items())

            assert row == valid_results[i]

    def test_post_process_binary_variables(self):
        headers = ['test1', 'test2', 'test3', 'test4']
        row = [1, 2, 0, '']

        conversion_map = ['test1', 'test2', 'test3', 'test4']

        AdultSymptomPrep.post_process_binary_variables(headers, row, conversion_map)

        assert row == [1, 0, 0, 0]
