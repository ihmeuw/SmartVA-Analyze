import pytest

from smartva import workerthread

@pytest.fixture
def worker_thread(tmpdir):
    out_dname = str(tmpdir.mkdir('out'))
    def completion_callback(a,b):
        pass

    return workerthread.WorkerThread('in', out_dname, {}, '', completion_callback)
    
class TestWorkerThread(object):
    def test_format_headers(self, worker_thread):
        headers = ['header', 'foo-header', 'bar-baz-header', 'foo:header', 'bar:baz:header']
        
        for h in headers:
            assert worker_thread._format_header(h) == 'header', '{} is not a clean header'.format(h)

