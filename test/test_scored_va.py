import pytest

from smartva.tariff_prep import Record


def test_reporter():
    va = Record()
    print(va)


def test_censored_transfers_to_masked_on_init():
    va = Record(censored=(2, 3))
    assert 2 in va.masked
    assert 3 in va.masked


def test_single_censored_transfers_to_masked_on_setting():
    va = Record()
    assert not va.masked

    va.censored = 1
    assert 1 in va.masked
    assert va.censored == {1}


def test_multiple_censored_transfers_to_masked_on_setting():
    va = Record()
    va.censored = [0, 1, 2, 3]
    for x in range(4):
        assert x in va.masked
    assert va.censored == {0, 1, 2, 3}


def test_set_censored_multiple_times():
    va = Record()
    va.censored = 2
    assert va.censored == {2}
    assert 2 in va.masked

    va.censored = 3
    assert va.censored == {3}
    assert 3 in va.masked
