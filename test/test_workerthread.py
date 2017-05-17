from smartva.workerthread import WorkerThread


def test_format_headers():
    headers = ['header', 'foo-header', 'bar-baz-header', 'foo:header', 'bar:baz:header']

    for h in headers:
        assert WorkerThread._format_header(h) == 'header', '{} is not a clean header'.format(h)
