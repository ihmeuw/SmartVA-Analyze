import pytest

from smartva.data_prep import DataPrep


class Preppy(DataPrep):
    INPUT_FILENAME_TEMPLATE = 'preppy_input.csv'
    OUPUT_FILENAME_TEMPLATE = 'preppy_output.csv'


@pytest.fixture
def prep(tmpdir):
    return Preppy(tmpdir.strpath, short_form=False)


def test_malformed_jagged_csv(prep):
    data="""h1,h2,h3\nfoo,"""
    with open(prep.input_file_path(), 'wt') as f:
        f.write(data)

    _, matrix = prep.read_input_file(prep.input_file_path())
    assert all([isinstance(value, basestring)
                for row in matrix for value in row.values()])
