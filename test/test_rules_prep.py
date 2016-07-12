import pytest

from smartva.rules_prep import RulesPrep


@pytest.fixture
def prep():
    return RulesPrep('', True)


class TestRulesPrep(object):
    def test_instance(self, prep):
        assert isinstance(prep, RulesPrep)
