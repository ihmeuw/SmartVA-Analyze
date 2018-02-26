import csv
import os
import subprocess

from smartva.config import basedir
from smartva.data import common_data
from smartva.data.adult_pre_symptom_data import VAR_CONVERSION_MAP as ADULT_VARS
from smartva.data.child_pre_symptom_data import VAR_CONVERSION_MAP as CHILD_VARS
from smartva.data.neonate_pre_symptom_data import VAR_CONVERSION_MAP as NEONATE_VARS


def test_invalid_inputs(tmpdir):
    headers = set()
    for var_map in (ADULT_VARS, CHILD_VARS, NEONATE_VARS):
        headers.update(var_map.keys())
    headers.update(common_data.SHORT_FORM_ADDITIONAL_HEADERS_DATA.keys())
    headers.update(common_data.BINARY_CONVERSION_MAP.keys())
    headers.add('gen_5_4d')
    headers = list(headers)

    base_row = {h: 'XXX' for h in headers}   # garbage values everywhere
    # Add consent and remove extraneous age variables
    base_row.update({
        'gen_3_1': '1',
        'gen_5_4a': '',
        'gen_5_4b': '',
        'gen_5_4c': '',
        'gen_5_4d': ''
    })

    # Force rows into each module
    adult_row = base_row.copy()
    adult_row.update({'sid': 'adult', 'gen_5_4a': '40'})

    child_row = base_row.copy()
    child_row.update({'sid': 'child', 'gen_5_4a': '3'})

    # To test the weight symptoms, we need an examine date later than the
    # birthdate. Both dates and the weight must be present and valid.
    child_row2 = child_row.copy()
    child_row2.update({'gen_5_1a': 2000, 'gen_5_1b': 1, 'gen_5_1c': 1,
                       'child_5_6b': 2002, 'child_5_6c': 1, 'child_5_6d': 1,
                       'child_5_6f': 1000, 'sid': 'child2'})

    neonate_row = base_row.copy()
    neonate_row.update({'sid': 'neonate', 'gen_5_4c': '3'})

    data = [adult_row, child_row, child_row2, neonate_row]

    input_file = tmpdir.join('sample_test.csv')
    with input_file.open('w') as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows([[row.get(h, '') for h in headers] for row in data])

    out_dir = tmpdir.mkdir('out')

    subprocess.call([
        'python', os.path.join(os.path.dirname(basedir), 'app.py'),
        input_file.strpath, out_dir.strpath
    ])
    results_dir = out_dir.join('1-individual-cause-of-death')

    for module in ('adult', 'child', 'neonate'):
        with results_dir.join('{}-predictions.csv'.format(module)).open() as f:
            assert len([row for row in f])
