import csv
import os
import subprocess

import pytest

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'app.py')
REQUIRED_HEADERS = ('gen_5_4a', 'gen_5_4b', 'gen_5_4c', 'gen_5_4d')


"""
Test cases:
1) age given in days with no endorsements
2) age group given, no days, with no endorsements. Should default to age zero
3) age in days == 0 and said never cried, breathed, moved (stillbirth rule)
4) only age group given and said never cried, breathed, moved (stillbirth rule)
5) age in days > 0 and said never cried, breathed, moved (stillbirth rule)
6) age in days == 0 with high tariff symptom for stillbirth, but didn't say
   never cried, breathed, moved
7) neonate age group with high tariff symptom for stillbirth, but didn't say
   never cried, breathed, moved. Age should default to 0
8-11) age in days > 0 with high tariff sympotm for stillbirth, but didn't say
   never cried, breathed, moved. Should be censored.
"""
@pytest.mark.parametrize('row, expected', [
    ({'sid': '1_age0', 'gen_5_4': 4, 'gen_5_4c': 0}, False),  # too little info
    ({'sid': '2_neonate_agegroup', 'gen_5_4d': 1}, False),  # too little info
    ({'sid': '3_never_age0', 'gen_5_4': 4, 'gen_5_4c': 0, 'child_1_15': 1},
     True),
    ({'sid': '4_never_agegroup', 'gen_5_4d': 1, 'child_1_15': 1}, True),
    ({'sid': '5_never_age5', 'gen_5_4': 4, 'gen_5_4c': 5, 'child_1_15': 1},
     False),   # conflicting info on VA
    ({'sid': '6_born_dead_age0', 'gen_5_4': 4, 'gen_5_4c': 0, 'child_1_11': 2},
     True),
    ({'sid': '7_born_dead_agegroup', 'gen_5_4d': 1, 'child_1_11': 2}, True),
    ({'sid': '8_born_dead_age1', 'gen_5_4': 4, 'gen_5_4c': 1,
      'child_1_11': 2}, False),   # conflicting info on VA
    ({'sid': '9_born_dead_age2', 'gen_5_4': 4, 'gen_5_4c': 2,
      'child_1_11': 2}, False),   # conflicting info on VA
    ({'sid': '10_born_dead_age3', 'gen_5_4': 4, 'gen_5_4c': 3,
      'child_1_11': 2}, False),   # conflicting info on VA
    ({'sid': '11_born_dead_age4', 'gen_5_4': 4, 'gen_5_4c': 4,
      'child_1_11': 2}, False),   # conflicting info on VA
], ids=lambda x: x['sid'])
def test_stillbirth_rules(tmpdir, tmpdir_factory, row, expected):
    data = dict(zip(REQUIRED_HEADERS, [''] * len(REQUIRED_HEADERS)))
    data.update(row)   # ensure age data is copied and not overwritten

    csvfile = tmpdir.join('sample_test.csv')
    with csvfile.open('w') as f:
        w = csv.writer(f)
        w.writerows(zip(*data.items()))

    infile = csvfile.strpath
    outdir = tmpdir_factory.mktemp('out').strpath
    subprocess.call(['python', APP, infile, outdir])

    with open(os.path.join(outdir, 'neonate-predictions.csv')) as f:
        predictions = [row for row in csv.DictReader(f)]

    assert len(predictions) == 1
    stillbirth = predictions[0]['cause34'] == 'Stillbirth'
    assert stillbirth is expected
