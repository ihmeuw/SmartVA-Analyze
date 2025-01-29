"""Functional testing for symptom extraction.

This is the test setup for verifying the mapping from ODK format to symptoms.
Test cases consist of an in-memory data set that is saved to disk a used as
the input file for smartva called from the cli in a subprocess. After analysis,
the output symptoms files are read in and specific symptom values are compared
with the expected results.

To set up a test case, create a list of dicts where each dict has, at a
minimum, the following keys: 'sid', 'symptom', 'endorsed' and 'module'. All
other keys are interpreted as columns from ODK input data. 'sid' is used as
the test ID and gives a short description of what is being tested. 'symptom'
is the name of symptom you intend to check. 'endorsed' should be True or False
indicating the expected value of the given symptom. 'module' is needed to
determine where to find the row in the output files.

Currently, this is set up to read data from modules in the same directory. The
headers for the saved data will be calculated so there is no need to have
every key for every row. Only include the values necessary for the test. The
`data` fixture is parametrized by other fixtures that each import,
post-process, and return the data. To add a test case, define a fixture that
return the data and add the string of the fixture name to the list of params
for the `data` fixture.

"""
from collections import defaultdict
import csv
import logging
import subprocess
import os
import warnings

import pytest

from smartva.output_prep import FOLDER4
from smartva.config import basedir


def make_valid(row):
    # Assume that we are verifying an endorsement (as the default)
    if 'endorsed' not in row:
        row['endorsed'] = True
    else:
        # It's important that "endorsed" be a bool instead of merely truthy
        # We are using the more strict `is` test to verify correctness
        row['endorsed'] = bool(row['endorsed'])

    if 'sid' not in row or 'symptom' not in row or 'module' not in row:
        raise KeyError('Rows must contain "sid", "symptom", "module" and '
                       '"endorsed"')

    return row


def make_valid_phmrc(row):
    """Add standard PHMRC specific values for a row of data"""

    row['gen_3_1'] = 1   # All rows need valid consent

    # Ensure that there is enough data to classify each row into a specific
    # module. Otherwise the rows are filtered out
    modules = {'adult': 3, 'child': 2, 'neonate': 1}
    row['gen_5_4d'] = modules[row['module']]

    return make_valid(row)


def make_valid_who(row):
    """Add standard WHO specific values for a row of data"""

    row['Id10013'] = 'yes'   # All rows need valid consent

    # Ensure that there is enough data to classify each row into a specific
    # module. Otherwise the rows are filtered out
    row['is{}'.format(row['module'].title())] = 1

    # Hack to support auto detect. There must be enough columns that look
    # like WHO indicator columns or we assume it's PHMRC data.
    for i in range(10000, 10050):
        col = 'Id{}'.format(i)
        if col not in row:
            row[col] = ''

    return make_valid(row)


def make_valid_who2016(row):
    """Add standard WHO2016 specific values for a row of data"""
    valid_row = make_valid_who(row)
    valid_row['Id10219'] = 'yes'   # Riley used the presence of this column to determine that the form is who2016
    return valid_row
    

def make_valid_who2022(row):
    """Add (and remove) standard WHO2022 specific values for a row of data"""
    valid_row = make_valid_who(row)
    if 'Id10219' in valid_row:
        del valid_row['Id10219']   # Riley used the absence of this column to determine that the form is who2022
    return valid_row


@pytest.fixture(scope='module')
def phmrc_adult():
    from .phmrc_adult_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'adult'
        make_valid_phmrc(row)
    return MAPPING


@pytest.fixture(scope='module')
def phmrc_child():
    from .phmrc_child_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'child'
        make_valid_phmrc(row)
    return MAPPING


@pytest.fixture(scope='module')
def phmrc_neonate():
    from .phmrc_neonate_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'neonate'
        make_valid_phmrc(row)
    return MAPPING


@pytest.fixture(scope='module')
def phmrc_freetext():
    from .phmrc_freetext_mapping import MAPPING
    return MAPPING


@pytest.fixture(scope='module')
def phmrc_checklist_words():
    from .phmrc_checklist_words_mapping import MAPPING
    return MAPPING


@pytest.fixture(scope='module')
def phmrc_ages():
    from .phmrc_age_mapping import MAPPING
    for row in MAPPING:
        make_valid(row)
    return MAPPING


@pytest.fixture(scope='module')
def phmrc_gated():
    from .phmrc_gated_mapping import MAPPING
    for row in MAPPING:
        make_valid_phmrc(row)
    return MAPPING


@pytest.fixture(scope='module')
def who_ages():
    # Hack to support auto detect. There must be enough columns that look
    # like WHO indicator columns or we assume it's PHMRC data.
    who_cols = {'Id{}'.format(i): '' for i in range(10000, 10050)}
    from .who_age_mapping import MAPPING
    for row in MAPPING:
        make_valid(row)
        row.update(who_cols)
    return MAPPING


@pytest.fixture(scope='module')
def who2016_adult():
    from .who2016_adult_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'adult'
        make_valid_who2016(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2016_child():
    from .who2016_child_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'child'
        make_valid_who2016(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2016_neonate():
    from .who2016_neonate_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'neonate'
        make_valid_who2016(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2016_freetext():
    from .who2016_freetext_mapping import MAPPING
    for row in MAPPING:
        make_valid_who2016(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2022_adult():
    from .who2022_adult_mapping import MAPPING
    for row in MAPPING:
        row['module'] = 'adult'
        make_valid_who2022(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2022_child():
    from .who2016_child_mapping import MAPPING  # reuse 2016 mapping, since it seems to exercise same parts
    for row in MAPPING:
        row['module'] = 'child'
        make_valid_who2022(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2022_neonate():
    from .who2022_neonate_mapping import MAPPING  # i copied the 2016 mapping and commented out a section that does not appear in the who 2022 instrument
    for row in MAPPING:
        row['module'] = 'neonate'
        make_valid_who2022(row)
    return MAPPING


@pytest.fixture(scope='module')
def who2022_freetext():
    from .who2016_freetext_mapping import MAPPING  # reuse 2016 mapping, since it seems to exercise same parts
    for row in MAPPING:
        make_valid_who2022(row)
    return MAPPING


@pytest.fixture(params=[
    'phmrc_adult',
    'phmrc_child',
    'phmrc_neonate',
    'phmrc_freetext',
    'phmrc_checklist_words',
    'phmrc_ages',
    'phmrc_gated',
    'who_ages',
    'who2016_adult',
    'who2016_child',
    'who2016_neonate',
    'who2016_freetext',
    'who2022_adult',
    'who2022_child',
    'who2022_neonate',
    'who2022_freetext',
])
def data(request, tmpdir):
    headers = {'gen_5_4a', 'gen_5_4b', 'gen_5_4c', 'gen_5_4d'}
    expected = defaultdict(list)
    input_data = request.getfixturevalue(request.param)
    for row in input_data:
        headers.update(list(row.keys()))
        expected[row['module']].append(
            {key: row[key] for key in ['sid', 'symptom', 'endorsed']}
        )
    headers = sorted(headers)

    filepath = tmpdir.join('input_data.csv').strpath
    with open(filepath, 'wt', newline='') as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        writer.writerows(input_data)

    return filepath, expected


def test_symptoms_exist_on_tariff_matrix(data):
    _, expected = data
    for module, rows in list(expected.items()):
        tested_symptoms = {row['symptom'] for row in rows}
        tariffs = os.path.join(basedir, 'data', 'tariffs-{}.csv'.format(module))
        with open(tariffs, 'rt') as f:
            symptoms = set(next(csv.reader(f))[1:])

        untested_symptoms = symptoms - tested_symptoms
        extra_symptoms = tested_symptoms - symptoms
        assert not extra_symptoms
        warnings.warn('There are {} untested symptoms: {}'.format(
            len(untested_symptoms), sorted(untested_symptoms)))


def test_symptom_extraction(tmpdir_factory, data):
    # Test cases all share the same logger object which is not cleaned up by
    # pytest after each test. For subsequent test cases, the logger receives
    # duplicated data for each previous test. This results in massive I/O for
    # logging as the number of cases increase. Disabling all logging prevents
    # this and allow test to complete in a reasonable amount of time.
    logging.disable(logging.CRITICAL)

    filename, expected_results = data

    outdir = tmpdir_factory.mktemp('out').strpath
    subprocess.call([
        'python',
        os.path.join(os.path.abspath(__file__).rsplit(os.sep, 3)[0], 'app.py'),
        filename,
        outdir,
    ])

    # I'm choosing to collect all errors instead failing fast with the first
    # error. This will allow us to drop into the debugger upon failing and
    # find every failing test case.
    errors = []
    for module, expected in list(expected_results.items()):
        symptom_file = os.path.join(outdir, FOLDER4, 'intermediate-files',
                                    '{}-symptom.csv'.format(module))

        with open(symptom_file, 'rt') as f:
            reader = csv.DictReader(f)

            for row in expected:
                actual = next(reader)
                value = actual.get(row['symptom'])
                if (not value or
                        row['sid'] != actual['sid'] or
                        bool(int(value)) is not row['endorsed']):
                    errors.append(row)
    assert len(errors) == 0, errors


@pytest.fixture(params=[
    ('adult', ['phmrc_adult', 'phmrc_freetext', 'phmrc_ages']),
    ('child', ['phmrc_child', 'phmrc_freetext', 'phmrc_ages']),
    ('neonate', ['phmrc_neonate', 'phmrc_freetext', 'phmrc_ages']),
])
def suite(request):
    module, suites = request.param
    cases = {
        case['symptom']
        for suite in suites
        for case in request.getfixturevalue(suite)
        if case['endorsed']
    }
    return module, cases


def test_symptom_mapping_coverage(suite):
    module, cases = suite
    tariffs = os.path.join(basedir, 'data', 'tariffs-{}.csv'.format(module))
    with open(tariffs, 'rt') as f:
        symptoms = set(next(csv.reader(f))[1:])

    # Known errors where the tariff matrix still contains something obsolete
    exceptions = {
        'neonate': {
            's15',   # duplicate sex
            # stillbirth abnormalities
            's20', 's21', 's22', 's23', 's24', 's25', 's26', 's27',
            's56991',   # duplicate delivery location
        }
    }
    diff = symptoms - cases - exceptions.get(module, set())
    # In other words, ensure that each symptom as at least one test
    # demonstrating that we can get a positive endorsement using ODK data.
    # All symptoms on the tariff matrix should be reachable
    assert not diff
