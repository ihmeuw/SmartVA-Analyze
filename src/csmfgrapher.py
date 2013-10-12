#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import sys
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import wx

import workerthread

# default dict for csmf graph
def get_default_dict():

    default_dict = dict()
    for module in module_labels:
        default_dict[module] = dict()
    return default_dict

# convert value from csv to key for dict
def get_gender_key(gender_value):

    gender_key = 'unknown'
    if gender_value == 1:
        gender_key = 'female'
    elif gender_value == 0:
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

# make and save csmf graph
def make_graph(module_key, output_dir):

    cause_keys = graph_data[module_key].keys()
    cause_fractions = graph_data[module_key].values()

    graph_title = module_key.capitalize() + ' CSMF'
    graph_filename = graph_title.replace(' ','-').lower()

    max_value = 1
    xlocations = np.arange(len(cause_keys)) # the x locations for the groups

    bar_width = .75 # the width of the bars

    # interactive mode off
    plt.ioff()
    fig, ax = plt.subplots()

    ax.set_title(graph_title)
    ax.set_ylabel('Mortality fractions')
    ax.yaxis.grid()

    ax.set_xticklabels(cause_keys,rotation=90)
    ax.set_xticks(xlocations)

    ax.bar(xlocations, cause_fractions, bar_width, color='#C44440',align='center')

    #add whitespace at top of bar
    ax.set_ylim(top=max_value)

    #add whitespace before first bar and after last
    plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

    #add some spacing for rotated xlabels
    plt.subplots_adjust(bottom=0.60)

    plt.savefig(output_dir + os.sep + graph_filename +'-figure.png',dpi=150)

    # clear the current figure
    plt.clf()

    # plt.close() causes a crash in os x.
    if sys.platform == 'darwin':
        del fig # cleans up the memory
    else:
        plt.close()

# labels for dict
global module_labels
module_labels = ('adult','child','neonate')

# build ordered dict for values to be graphed. indexed by module
global graph_data
graph_data = get_default_dict()

class CSMFGrapher():

    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.want_abort = 0

    def run(self):

        updatestr = 'Making CSMF graphs\n'
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

        graph_data_unsorted = get_default_dict()

        module_errors = {}
        for module_key in module_labels:

            # read and process data from csv. rU gives universal newline support
            # TODO what happens if you don't have a module
            try:
                csv_file = csv.DictReader(open(self.inputFilePath.replace('$module-csmf.csv', module_key +'-csmf.csv'),'rU'))

                module_errors[module_key] = 0

                for row in csv_file:
                    if self.want_abort == 1:
                        return

                    cause_key = row['cause'].rstrip()
                    cause_fraction = row['percentage']

                    graph_data_unsorted[module_key][cause_key] = float(cause_fraction)

            except IOError:
                # if the file isn't there, there was no data or an error, so just skip it
                # print module_key+'-csmf.csv not found'
                module_errors[module_key] = 1

        # make csmf graphs
        for module_key in module_labels:
            if module_errors[module_key] != 1:
                # sort data in decreasing order
                graph_data[module_key] = OrderedDict(sorted(graph_data_unsorted[module_key].iteritems(), key=lambda x: x[1],reverse=True))
                make_graph(module_key,self.output_dir)

        updatestr = 'Finished making CSMF graphs\n'
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
    
    def abort(self):
        self.want_abort = 1