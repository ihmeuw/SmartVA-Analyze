import csv
import os
import re
from collections import defaultdict
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import wx

import workerthread


# labels for dict
module_labels = ('adult', 'child', 'neonate')
age_labels = ('0-28 days', '29 days - 1 year', '1-4 years', '5-11 years', '12-19 years', '20-44 years', '45-59 years', '60+ years', 'unknown')
gender_labels = ('male', 'female', 'unknown')


# default dict for cause of death graph
def get_default_dict():
    default_dict = dict()
    for gender in gender_labels:
        default_dict[gender] = OrderedDict.fromkeys(age_labels, 0)
    return default_dict


# build ordered dict for values to be graphed. indexed by cause, the gender, then age.
graph_data = defaultdict(get_default_dict)


# convert value from csv to key for dict
def get_gender_key(gender_value):
    gender_key = 'unknown'
    if gender_value == '1':
        gender_key = 'female'
    elif gender_value == '0':
        gender_key = 'male'
    return gender_key


# convert value from csv to key for dict
def get_age_key(module_key, age_value):
    age_key = 'unknown'
    # TODO are age values correct for neonate and child?
    if module_key == 'neonate' and (age_value >= 0 and age_value <= 28):
        age_key = '0-28 days'
    elif module_key == 'child' and (age_value > 0 and age_value < 12):
        age_key = '29 days - 1 year'
    elif module_key == 'adult' and (age_value >= 1 and age_value <= 4):
        age_key = '1-4 years'
    elif module_key == 'adult' and (age_value >= 5 and age_value <= 11):
        age_key = '5-11 years'
    elif module_key == 'adult' and (age_value >= 12 and age_value <= 19):
        age_key = '12-19 years'
    elif module_key == 'adult' and (age_value >= 20 and age_value <= 44):
        age_key = '20-44 years'
    elif module_key == 'adult' and (age_value >= 45 and age_value <= 59):
        age_key = '45-59 years'
    elif module_key == 'adult' and (age_value >= 60):
        age_key = '60+ years'
    return age_key


# make and save cause graph
def make_graph(cause_key, output_dir):
    male_data = graph_data[cause_key]['male'].values()
    female_data = graph_data[cause_key]['female'].values()
    unknown_data = graph_data[cause_key]['unknown'].values()

    graph_title = cause_key.capitalize() + ' by age and sex'
    graph_filename = re.sub('[^\w_\. ]', '-', cause_key.replace('(', '').replace(')', '')).replace(' ', '-').lower()

    max_value = max(max(male_data), max(female_data), max(unknown_data))
    xlocations = np.arange(len(age_labels))  # the x locations for the groups

    bar_width = 0.25  # the width of the bars

    # interactive mode off
    plt.ioff()
    fig, ax = plt.subplots()

    rects1 = ax.bar(xlocations, male_data, bar_width, color='#C44440', align='center')
    rects2 = ax.bar(xlocations + bar_width, female_data, bar_width, color='#1D72AA', align='center')

    ax.set_title(graph_title)
    ax.set_ylabel('Number of VAs')
    ax.yaxis.grid()

    ax.set_xticklabels(age_labels, rotation=90)
    ax.set_xticks(xlocations + bar_width / 2)

    # push legend outside of the plot
    ax.legend((rects1[0], rects2[0]), gender_labels, loc='upper center', bbox_to_anchor=(0.5, -0.375), ncol=2)

    # add whitespace at top of bar
    ax.set_ylim(top=max_value + .5)

    # add whitespace before first bar and after last
    plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

    # add some spacing for rotated xlabels
    plt.subplots_adjust(bottom=0.35)

    # clean up filenames
    plt.savefig(output_dir + os.sep + graph_filename + '-figure.png', dpi=150)

    # clear the current figure
    plt.clf()
    plt.close()


class CauseGrapher(object):
    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.want_abort = 0

    def run(self):

        updatestr = 'Making cause graphs\n'
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

        module_errors = {}
        for module_key in module_labels:

            # read and process data from csv. rU gives universal newline support
            # TODO what happens if you don't have a module
            try:
                csv_file = csv.DictReader(
                    open(self.inputFilePath.replace('$module-predictions.csv', module_key + '-predictions.csv'), 'rU'))

                module_errors[module_key] = 0

                for row in csv_file:
                    if self.want_abort == 1:
                        return

                    age_key = get_age_key(module_key, float(row['age']))
                    gender_key = get_gender_key(row['sex'])
                    cause_key = row['cause34']

                    graph_data[cause_key][gender_key][age_key] += 1
                    graph_data['All'][gender_key][age_key] += 1

            except IOError:
                # if the file isn't there, there was no data or an error, so just skip it
                # print module_key+'-predictions.csv not found'
                module_errors[module_key] = 1

        # make cause of death graphs
        for cause_key in graph_data.keys():
            # TODO - Fix this. Module key may not be the correct variable here.
            if module_errors[module_key] != 1:
                make_graph(cause_key, self.output_dir)

        updatestr = 'Finished making cause graphs\n'
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

    def abort(self):
        self.want_abort = 1
