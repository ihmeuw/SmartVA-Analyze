import pytest


def pytest_addoption(parser):
    parser.addoption('--data-checks', action='store_true',
                     help='Run slow tests which verify saved data is correct.')
