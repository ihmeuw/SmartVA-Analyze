import logging
import os
import pytest
# import subprocess

from smartva.utils import status_notifier
from smartva.loggers import status_logger, warning_logger
from test_utils.status_handler import StatusHandler


@pytest.fixture
def warning_file(tmpdir):
    return os.path.abspath(tmpdir.join('warnings.txt').strpath)


@pytest.fixture
def status_file(tmpdir):
    return os.path.abspath(tmpdir.join('status.txt').strpath)


def test_loggers(warning_file, status_file, tmpdir):
    # subprocess.call(['open', tmpdir.strpath])
    status_logger.addHandler(logging.FileHandler(status_file, mode='w'))
    status_notifier.register(StatusHandler(status_logger.info))
    warning_logger.addHandler(logging.FileHandler(warning_file, mode='w'))
