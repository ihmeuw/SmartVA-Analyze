import pytest
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_addoption(parser):
    parser.addoption(
        '--data-checks',
        action='store_true',
        default=False,
        help='Run slow tests which verify saved data is correct.'
    )

def pytest_collection_modifyitems(config, items):
    # If --data-checks is NOT given, skip tests marked with "data_checks"
    if not config.getoption("--data-checks"):
        skip_marker = pytest.mark.skip(reason="need --data-checks option to run")
        for item in items:
            if "data_checks" in item.keywords:
                item.add_marker(skip_marker)
