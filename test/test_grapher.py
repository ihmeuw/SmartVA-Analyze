from collections import defaultdict, OrderedDict
import numpy as np
import matplotlib.pyplot as plt


import pytest


from smartva import cause_grapher
from smartva.data.common_data import MALE, FEMALE
from smartva.tariff_prep import TariffPrep, Record
from smartva.data import adult_tariff_data


@pytest.fixture
def prep(tmpdir):
    return TariffPrep(
        adult_tariff_data,
        working_dir_path=tmpdir.strpath,
        short_form=True,
        options={'hce': True, 'free_text': True, 'hiv': True, 'malaria': True,
                 'chinese': False},
        country='USA'
    )


def test_get_default_dict():
    valid_d = {
        'test': {
            MALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0),
            FEMALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0)
        }
    }

    d = defaultdict(cause_grapher.get_default_dict)
    d['test']  # Evoke the default dict.

    assert d == valid_d


def test_get_default_dict_inc():
    valid_d = {
        'test': {
            MALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0),
            FEMALE: OrderedDict.fromkeys(reversed(cause_grapher.AGE_DATA.values()), 0)
        }
    }
    valid_d['test'][MALE]['0-28 days'] += 1

    d = defaultdict(cause_grapher.get_default_dict)
    d['test'][MALE]['0-28 days'] += 1

    assert d == valid_d


def test_get_age_key_12_19():
    assert cause_grapher.get_age_key(12) == '12-19 years'
    assert cause_grapher.get_age_key(19.9) == '12-19 years'


@pytest.mark.parametrize('age, label', [
    (0, '0-28 days'),
    (12. / 365, '0-28 days'),
    (28. / 365, '0-28 days'),
    (29. / 365, '29 days - 1 year'),
    (77. / 365, '29 days - 1 year'),
    (364. / 365, '29 days - 1 year'),
    (1, '1-4 years'),
    (3, '1-4 years'),
    (4.99999, '1-4 years'),
    (5, '5-11 years'),
    (7, '5-11 years'),
    (11.99999, '5-11 years'),
    (12, '12-19 years'),
    (17, '12-19 years'),
    (19.99999, '12-19 years'),
    (20, '20-29 years'),
    (27, '20-29 years'),
    (29.99999, '20-29 years'),
    (30, '30-39 years'),
    (37, '30-39 years'),
    (39.99999, '30-39 years'),
    (40, '40-49 years'),
    (47, '40-49 years'),
    (49.99999, '40-49 years'),
    (50, '50-59 years'),
    (57, '50-59 years'),
    (59.99999, '50-59 years'),
    (60, '60-69 years'),
    (67, '60-69 years'),
    (69.99999, '60-69 years'),
    (70, '70-79 years'),
    (77, '70-79 years'),
    (79.99999, '70-79 years'),
    (80, '80+ years'),
    (87, '80+ years'),
    (125, '80+ years'),
    (-1, 'Unknown'),
])
def test_get_age_key(age, label):
    assert cause_grapher.get_age_key(age) == label


def test_csmf_sex_undetermined_plot(prep):
    """
    Redistributed CSMFs for undetermined causes of death should not include
    biologically impossible causes for males and females. Check that these
    causes are not included in the CSMF figures.
    """

    # male and female user data with undetermined cause and age zero (unknown age)
    user_data_male = [Record('sid{}'.format(i), age=0, sex=1, cause34_name='Undetermined')
                        for i in range(7)]
    user_data_female = [Record('sid{}'.format(i), age=0, sex=2, cause34_name='Undetermined')
                        for i in range(7)]
    user_data_unknown = [Record('sid{}'.format(i), age=0, sex=0, cause34_name='Undetermined')
                        for i in range(7)]

    user_data = user_data_male + user_data_female + user_data_unknown

    undetermined_weights = prep._get_undetermined_matrix()
    csmf, csmf_by_sex = prep.calculate_csmf(user_data, undetermined_weights)

    for sex in range(1, 2):
        # input graph data
        graph_data = csmf_by_sex[sex]

        cause_keys = graph_data.keys()
        cause_fractions = graph_data.values()

        #graph_title = module_key.capitalize() + ' CSMF' # not neessary to have the graph title
        # graph_filename = graph_title.replace(' ', '-').lower() # not neccesary to have filename

        max_value = max(cause_fractions)
        xlocations = np.arange(len(cause_keys))  # the x locations for the groups

        bar_width = .75  # the width of the bars

        # Interactive mode off.
        plt.ioff()
        fig, ax = plt.subplots()

        ax.set_ylabel('Mortality fractions')
        ax.yaxis.grid()

        ax.set_xticklabels(cause_keys)
        ax.set_xticks(xlocations)

        bar_width = .75  # the width of the bars

        # Interactive mode off.
        plt.ioff()
        fig, ax = plt.subplots()

        #ax.set_title(graph_title) # not neessary to have the graph title
        ax.set_ylabel('Mortality fractions')
        ax.yaxis.grid()

        ax.set_xticklabels(cause_keys, rotation=90)
        ax.set_xticks(xlocations)

        ax.bar(xlocations, cause_fractions, bar_width, color='#C44440', align='center')

        # Add whitespace at top of bar.
        ax.set_ylim(top=max_value + max_value * 0.1)

        # Add whitespace before first bar and after last.
        plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

        # Add some spacing for rotated xlabels.
        plt.subplots_adjust(bottom=0.60)

        # neccessary to get acutally plot to get x-axis labels
        fig.canvas.draw()

        # list of x axis labels
        labels = [item.get_text() for item in ax.get_xticklabels()]

        # check biologically impossible causes
        if sex == 1:
            assert "Stroke" in labels
            assert "Prostate Cancer" in labels
            assert "Maternal" not in labels

        if sex == 2:
            assert "Stroke" in labels
            assert "Maternal" in labels
            assert "Cervical Cancer" in labels
            assert "Prostate Cancer" not in labels

