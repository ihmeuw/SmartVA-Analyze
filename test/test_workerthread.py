import pytest

from smartva import workerthread

@pytest.fixture
def prep(tmpdir):
    return workerthread.WorkerThread('in', str(tmpdir.mkdir('out')), {}, '', False)
    
class TestWorkerThread(object):
    def test_format_headers(self, prep):
        headers = ['header', 'foo-header', 'bar-baz-header', 'foo:header', 'bar:baz:header']
        
        for h in headers:
            assert prep._format_header(h) == 'header', '{} is not a clean header'.format(h)

