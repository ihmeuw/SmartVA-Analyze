from smartva.utils.conversion_utils import additional_headers_and_values


def test_additional_headers_and_values():
    headers = ['SubmissionDate', 'interviewstarttime', 'interviewdate', 'gen_1_1', 'Intid', 'sid', 'ID']
    additional_headers_data = [
        ('test1', 0),
        ('test2', 0),
        ('test3', 0)
    ]

    additional_headers, additional_values = additional_headers_and_values(
        headers, additional_headers_data)

    assert additional_headers == [k for k, v in additional_headers_data]
    assert additional_values == [v for k, v in additional_headers_data]


def test_additional_headers_and_values_existing():
    headers = ['SubmissionDate', 'interviewstarttime', 'interviewdate', 'gen_1_1', 'Intid', 'sid', 'ID', 'test1']
    additional_headers_data = [
        ('test1', 0),
        ('test2', 0),
        ('test3', 0)
    ]

    additional_headers, additional_values = additional_headers_and_values(
        headers, additional_headers_data)

    assert additional_headers == [k for k, v in additional_headers_data if k not in headers]
    assert additional_values == [v for k, v in additional_headers_data if k not in headers]
