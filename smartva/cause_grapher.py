import csv
import os
import re
from collections import defaultdict, OrderedDict

import matplotlib.pyplot as plt
import numpy as np

from smartva.common_data import MALE, FEMALE, ADULT, CHILD, NEONATE
from smartva.loggers import status_logger
from smartva.utils import status_notifier

INPUT_FILENAME_TEMPLATE = '{:s}-predictions.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-figure.png'


# labels for dict
MODULE_LABELS = (ADULT, CHILD, NEONATE)

AGE_DATA = OrderedDict(
    (
        (60.0, '60+ years'),
        (45.0, '45-59 years'),
        (20.0, '20-44 years'),
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
        default_dict[gender] = OrderedDict.fromkeys(reversed(AGE_DATA.values()), 0)
    return default_dict


def get_age_key(age_value):
    """Helper function to identify age group by age.

    :param age_value: Age in years.
    :return: String representation of age group.
    """
    for k, v in AGE_DATA.items():
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
    male_data = graph_data[MALE].values()
    female_data = graph_data[FEMALE].values()

    graph_title = cause_key.capitalize() + ' by age and sex'
    graph_filename = re.sub('[^\w_\. ]', '-', cause_key.replace('(', '').replace(')', '')).replace(' ', '-').lower()

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

    ax.set_xticklabels(reversed(AGE_DATA.values()), rotation=90)
    ax.set_xticks(xlocations + bar_width / 2)

    # Push legend outside of the plot.
    ax.legend((rects1[0], rects2[0]), GENDER_DATA.values(), loc='upper center', bbox_to_anchor=(0.5, -0.375), ncol=2)

    # Add whitespace at top of bar.
    ax.set_ylim(top=max_value + .5)

    # Add whitespace before first bar and after last.
    plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

    # Add some spacing for rotated xlabels.
    plt.subplots_adjust(bottom=0.35)

    # Save graph figure.
    plt.savefig(os.path.join(output_dir, OUTPUT_FILENAME_TEMPLATE.format(graph_filename)), dpi=150)

    # Clear the current figure.
    plt.clf()
    plt.close()


class CauseGrapher(object):
    """Generate and save a graph for each cause, and one for all causes."""

    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.want_abort = False

    def run(self):
        status_logger.info('Making cause graphs')
        status_notifier.update({'progress': 1})

        graph_data = defaultdict(get_default_dict)

        status_notifier.update({'sub_progress': (0, len(MODULE_LABELS))})

        for cnt, module_key in enumerate(MODULE_LABELS):
            status_notifier.update({'sub_progress': (cnt,)})

            try:
                with open(os.path.join(self.input_dir, INPUT_FILENAME_TEMPLATE.format(module_key)), 'rb') as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        if self.want_abort:
                            return

                        age_key = get_age_key(float(row['age']))
                        sex_key = int(row['sex'])

                        graph_data[row['cause34']][sex_key][age_key] += 1
                        graph_data['All'][sex_key][age_key] += 1

            except IOError:
                # The file isn't there, there was no data or an error, so just skip it.
                continue

        # Make cause of death graphs.
        status_notifier.update({'sub_progress': (0, len(graph_data))})

        for cnt, (cause_key, data) in enumerate(graph_data.items()):
            status_notifier.update({'sub_progress': (cnt,)})

            make_graph(data, cause_key, self.output_dir)

        status_notifier.update({'sub_progress': None})

    def abort(self):
        self.want_abort = True
