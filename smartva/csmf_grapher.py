import csv
import os
from collections import OrderedDict, defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from smartva.data.common_data import ADULT, CHILD, NEONATE
from smartva.grapher_prep import GrapherPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier

INPUT_FILENAME_TEMPLATE = '{:s}-csmf.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-figure.png'

MODULE_LABELS = (ADULT, CHILD, NEONATE)


def make_graph(graph_data, module_key, output_dir):
    """Generate and save a cause graph.

    :param graph_data: Graph data dict.
    :param module_key: Name of the module for which to generate graph.
    :param output_dir: Directory in which to save graph.
    """
    cause_keys = graph_data.keys()
    cause_fractions = graph_data.values()

    graph_title = module_key.capitalize() + ' CSMF'
    graph_filename = graph_title.replace(' ', '-').lower()

    max_value = max(cause_fractions)
    xlocations = np.arange(len(cause_keys))  # the x locations for the groups

    bar_width = .75  # the width of the bars

    # Interactive mode off.
    plt.ioff()
    fig, ax = plt.subplots()

    ax.set_title(graph_title)
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

    # Save graph figure.
    plt.savefig(os.path.join(output_dir, OUTPUT_FILENAME_TEMPLATE.format(graph_filename)), dpi=150)

    # Clear the current figure.
    plt.clf()
    plt.close()


class CSMFGrapher(GrapherPrep):
    """Generate and save a graph for each group's mortality fraction."""

    def _update_status(self):
        super(CSMFGrapher, self)._update_status()
        status_logger.info('Making CSMF graphs')
        status_notifier.update({'progress': 1})

    def _read_graph_data(self):
        super(CSMFGrapher, self)._read_graph_data()
        # build ordered dict for values to be graphed. indexed by module
        graph_data_unsorted = defaultdict(dict)

        status_notifier.update({'sub_progress': (0, len(MODULE_LABELS))})

        for cnt, module_key in enumerate(MODULE_LABELS):
            status_notifier.update({'sub_progress': (cnt,)})

            try:
                with open(os.path.join(self.input_dir_path, INPUT_FILENAME_TEMPLATE.format(module_key)), 'r') as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        self.check_abort()

                        cause_key = row['cause'].rstrip()
                        cause_fraction = row['CSMF']

                        graph_data_unsorted[module_key][cause_key] = float(cause_fraction)

            except IOError:
                # The file isn't there, there was no data or an error, so just skip it
                continue

            for sex in ('male', 'female'):
                try:
                    key = '-'.join([module_key, sex])
                    filename = os.path.join(self.input_dir_path,
                                            '{:s}-csmf.csv'.format(key))
                    with open(filename, 'r') as f:
                        for row in csv.DictReader(f):
                            self.check_abort()

                            cause_key = row['cause'].rstrip()
                            cause_fraction = row['CSMF']

                            graph_data_unsorted[key][cause_key] = float(cause_fraction)
                except IOError:
                    continue

        return graph_data_unsorted

    def _make_graphs(self, graph_data_unsorted):
        super(CSMFGrapher, self)._make_graphs(graph_data_unsorted)
        # Make csmf graphs.
        status_notifier.update({'sub_progress': (0, len(graph_data_unsorted))})

        for cnt, (module_key, data) in enumerate(graph_data_unsorted.items()):
            self.check_abort()

            status_notifier.update({'sub_progress': (cnt,)})

            # sort data in decreasing order
            graph_data = OrderedDict(sorted(data.items(), key=lambda x: x[1], reverse=True))
            make_graph(graph_data, module_key, self.output_dir_path)
            
        status_notifier.update({'sub_progress': None})
