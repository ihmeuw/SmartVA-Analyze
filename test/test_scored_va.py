import pytest

from smartva.tariff_prep import ScoredVA

def test_reporter():
    x = ScoredVA({}, 0, 'sid', 0, 1, [])
    print x
