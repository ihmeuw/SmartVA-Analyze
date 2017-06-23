import csv
import os
import subprocess

import pytest

from smartva.data.common_data import SYMPTOM_AGE_KEY
from smartva.data.adult_symptom_data import DEFAULT_AGE as adult_default_age
from smartva.data.child_symptom_data import DEFAULT_AGE as child_default_age
from smartva.data.neonate_symptom_data import DEFAULT_AGE as neonate_default_age


DEFAULT_AGES = {
    'adult': adult_default_age,
    'child': child_default_age,
    'neonate': neonate_default_age,
}
APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'app.py')
CMD = 'python {app} {infile} {outdir}'


@pytest.fixture
def row():
    return {'gen_3_1': 1, 'gen_5_4a': '', 'gen_5_4b': '', 'gen_5_4c': '',
            'gen_5_4d': ''}


@pytest.mark.parametrize('update, module', [
    ({'sid': 'adult-agegroup', 'gen_5_4d': 3}, 'adult'),
    ({'sid': 'child-agegroup', 'gen_5_4d': 2}, 'child'),
    ({'sid': 'neonate-agegroup', 'gen_5_4d': 1}, 'neonate'),
], ids=lambda x: x['sid'])
def test_default_age(tmpdir, row, module, update):
    infile = tmpdir.join('input_data.csv').strpath
    outdir = tmpdir.mkdir('out').strpath
    age = DEFAULT_AGES.get(module)

    row.update(update)

    with open(infile, 'w') as f:
        csv.writer(f).writerows(zip(*row.items()))

    subprocess.call(CMD.format(app=APP, infile=infile, outdir=outdir).split())

    symptom_file = os.path.join(outdir, 'intermediate-files',
                                '{}-symptom.csv'.format(module))
    with open(symptom_file) as f:
        symp = [row for row in csv.DictReader(f)]

    with open(os.path.join(outdir, '{}-predictions.csv'.format(module))) as f:
        pred = [row for row in csv.DictReader(f)]

    assert float(symp[0][SYMPTOM_AGE_KEY]) == float(pred[0]['age']) == age
