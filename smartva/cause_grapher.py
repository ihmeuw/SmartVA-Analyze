import csv
import os
import re
from collections import defaultdict, OrderedDict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from smartva.data.common_data import MALE, FEMALE, ADULT, CHILD, NEONATE
from smartva.grapher_prep import GrapherPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier

INPUT_FILENAME_TEMPLATE = '{:s}-predictions.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-figure.png'

MODULE_LABELS = (ADULT, CHILD, NEONATE)

AGE_DATA = OrderedDict(
    (
        (80.0, '80+ years'),
        (70.0, '70-79 years'),
        (60.0, '60-69 years'),
        (50.0, '50-59 years'),
        (40.0, '40-49 years'),
        (30.0, '30-39 years'),
        (20.0, '20-29 years'),
        (12.0, '12-19 years'),
        (5.0, '5-11 years'),
        (1.0, '1-4 years'),
        (29 / 365.0, '29 days - 1 year'),
        (0.0, '0-28 days')
    )
)

GENDER_DATA = OrderedDict(
    (
        (MALE, 'male'),
        (FEMALE, 'female'),
    )
)


# default dict for cause of death graph
def get_default_dict():
    """Helper function to create a graph data default dict template.

    :return: Graph data default dict template.
    """
    default_dict = dict()
    for gender in GENDER_DATA:
        default_dict[gender] = OrderedDict.fromkeys(reversed(list(AGE_DATA.values())), 0)
    return default_dict


def get_age_key(age_value):
    """Helper function to identify age group by age.

    :param age_value: Age in years.
    :return: String representation of age group.
    """
    for k, v in list(AGE_DATA.items()):
        if age_value >= k:
            return v
    return 'Unknown'


# make and save cause graph
def make_graph(graph_data, cause_key, output_dir):
    """Generate and save a cause graph.

    :param graph_data: Graph data dict.
    :param cause_key: Name of the cause for which to generate graph.
    :param output_dir: Directory in which to save graph.
    """
    male_data = list(graph_data[MALE].values())
    female_data = list(graph_data[FEMALE].values())

    graph_title = cause_key.capitalize() + ' by age and sex'
    graph_filename = re.sub(r'[^\w_\. ]', '-', cause_key.replace('(', '').replace(')', '')).replace(' ', '-').lower()

    max_value = max(max(male_data), max(female_data))
    xlocations = np.arange(len(AGE_DATA))  # the x locations for the groups

    bar_width = 0.25  # the width of the bars

    # Interactive mode off.
    plt.ioff()
    fig, ax = plt.subplots()

    # Place male and female bars next to each other.
    rects1 = ax.bar(xlocations, male_data, bar_width, color='#C44440', align='center')
    rects2 = ax.bar(xlocations + bar_width, female_data, bar_width, color='#1D72AA', align='center')

    ax.set_title(graph_title)
    ax.set_ylabel('Number of VAs')
    ax.yaxis.grid()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    ax.set_xticklabels(list(reversed(list(AGE_DATA.values()))), rotation=90)
    ax.set_xticks(xlocations + bar_width / 2)

    # Push legend outside of the plot.
    ax.legend((rects1[0], rects2[0]), list(GENDER_DATA.values()), loc='upper center', bbox_to_anchor=(0.5, -0.375), ncol=2)

    # Add whitespace at top of bar.
    ax.set_ylim(top=max_value + max_value * 0.1)

    # Add whitespace before first bar and after last.
    plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

    # Add some spacing for rotated xlabels.
    plt.subplots_adjust(bottom=0.35)

    # Save graph figure.
    plt.savefig(os.path.join(output_dir, OUTPUT_FILENAME_TEMPLATE.format(graph_filename)), dpi=150)

    # Clear the current figure.
    plt.clf()
    plt.close()


class CauseGrapher(GrapherPrep):
    """Generate and save a graph for each cause, and one for all causes."""

    def _update_status(self):
        status_logger.info('Making cause graphs')
        status_notifier.update({'progress': 1})

    def _read_graph_data(self):
        graph_data = defaultdict(get_default_dict)
        status_notifier.update({'sub_progress': (0, len(MODULE_LABELS))})
        for cnt, module_key in enumerate(MODULE_LABELS):
            status_notifier.update({'sub_progress': (cnt,)})

            try:
                with open(os.path.join(self.input_dir_path, INPUT_FILENAME_TEMPLATE.format(module_key)), 'r') as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        self.check_abort()

                        try:
                            age_key = get_age_key(float(row['age']))
                            if age_key not in list(AGE_DATA.values()):
                                raise ValueError('Unknown age group.')
                            sex_key = int(row['sex'])
                            if sex_key not in [1,2]:
                                raise ValueError('Cannot yet plot when sex is not M/F')
                        except ValueError as e:
                            # Age or sex is invalid. Log warning and skip this item.
                            warning_logger.warning('Cause Grapher :: SID {} value for age or sex is invalid.'
                                                   .format(row['sid'], str(e)))
                            continue

                        graph_data[row['cause34']][sex_key][age_key] += 1
                        graph_data['All'][sex_key][age_key] += 1

            except IOError:
                # The file isn't there, there was no data or an error, so just skip it.
                continue

        return graph_data

    def _make_graphs(self, graph_data):
        # Make cause of death graphs.
        status_notifier.update({'sub_progress': (0, len(graph_data))})
        for cnt, (cause_key, data) in enumerate(graph_data.items()):
            self.check_abort()

            status_notifier.update({'sub_progress': (cnt,)})

            make_graph(data, cause_key, self.output_dir_path)
        status_notifier.update({'sub_progress': None})

