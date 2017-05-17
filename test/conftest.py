import pytest
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_addoption(parser):
    parser.addoption('--data-checks', action='store_true',
                     help='Run slow tests which verify saved data is correct.')
