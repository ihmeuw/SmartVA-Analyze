import csv
import os
import subprocess
import sys

import pytest

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'app.py')
CMD = 'python {app} {infile} {outdir} --hiv {hiv} --legacy-format'


@pytest.fixture
def aids_rule_data(tmpdir):
    csvfile = tmpdir.join('sample_test.csv')
    headers = ['sid', 'gen_5_4a', 'gen_5_4b', 'gen_5_4c', 'gen_5_4d',
               'child_5_17', 'child_5_18', 'child_5_19']
    data = [
        ['no-aids', 0, 0, 0, 2, 0, 0, 0],
        ['aids-positive', 0, 0, 0, 2, 1, 1, 1],
    ]

    with csvfile.open('w') as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(data)

    return csvfile.strpath


def test_aids_rule_with_aids_checked(tmpdir_factory, aids_rule_data):
    outdir = tmpdir_factory.mktemp('out').strpath

    command = CMD.format(app=APP, infile=aids_rule_data, outdir=outdir,
                         hiv='true')
    subprocess.call(command.split())

    with open(os.path.join(outdir, 'child-predictions.csv')) as f:
        predictions = [row for row in csv.DictReader(f)]

    assert predictions[0]['cause34'] != 'AIDS'
    assert predictions[1]['cause34'] == 'AIDS'


def test_aids_rule_with_aids_unchecked(tmpdir_factory, aids_rule_data):
    outdir = tmpdir_factory.mktemp('out').strpath

    command = CMD.format(app=APP, infile=aids_rule_data, outdir=outdir,
                         hiv='false')
    subprocess.call(command.split())

    with open(os.path.join(outdir, 'child-predictions.csv'), newline='') as f:
        predictions = [row for row in csv.DictReader(f)]

    assert predictions[0]['cause34'] != 'AIDS'
    assert predictions[1]['cause34'] != 'AIDS'
