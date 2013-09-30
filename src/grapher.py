#!/usr/bin/env python
import csv
import os
import re
import sys
from collections import defaultdict
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import wx

import workerthread

# default dict for cause of death graph
def get_default_cause_dict():

    default_dict = dict()
    for gender in gender_labels:
        default_dict[gender] = OrderedDict.fromkeys(age_labels, 0)
    return default_dict

# default dict for csmf graph
def get_default_csmf_dict():

    default_dict = dict()
    for module in module_labels:
        default_dict[module] = dict()
    return default_dict

# convert value from csv to key for dict
def get_gender_key(gender_value):

    gender_key = 'unknown'
    if gender_value == 1:
        gender_key = 'male'
    elif gender_value == 0:
        gender_key = 'female'
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
def make_cause_graph(cause_key, output_dir):

    male_data = cause_graph_data[cause_key]['male'].values()
    female_data = cause_graph_data[cause_key]['female'].values()
    unknown_data = cause_graph_data[cause_key]['unknown'].values()
    
    graph_title = cause_key +' deaths by age and gender'
    graph_filename = re.sub('[^\w\-_\. ]', ' ', cause_key).rstrip()

    max_value = max(max(male_data),max(female_data),max(unknown_data))
    xlocations = np.arange(len(age_labels))    # the x locations for the groups
    
    bar_width = 0.25 # the width of the bars

    # interactive mode off
    plt.ioff()
    fig, ax = plt.subplots()

    rects1 = ax.bar(xlocations, male_data, bar_width, color='#C44440',align='center')
    rects2 = ax.bar(xlocations+bar_width, female_data, bar_width, color='#1D72AA',align='center')

    ax.set_title(graph_title)
    ax.set_ylabel('number of VAs')
    ax.yaxis.grid()
    
    ax.set_xticklabels(age_labels,rotation=90)
    ax.set_xticks(xlocations+bar_width/2)

    #push legend outside of the plot
    ax.legend((rects1[0],rects2[0]), gender_labels,loc='upper center', bbox_to_anchor=(0.5, -0.375),ncol=2)
    
    #add whitespace at top of bar
    ax.set_ylim(top=max_value + .5)
    
    #add whitespace before first bar and after last
    plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

    #add some spacing for rotated xlabels
    plt.subplots_adjust(bottom=0.35)

    # clean up filenames
    plt.savefig(output_dir + os.sep + graph_filename+' graph.png',dpi=150)

    # clear the current figure
    plt.clf()

    # plt.close() causes a crash in os x.
    if sys.platform == 'darwin':
        del fig # cleans up the memory
    else:
        plt.close()


# make and save csmf graph
def make_csmf_graph(module_key, output_dir):

    cause_keys = csmf_graph_data[module_key].keys()
    case_count = sum(csmf_graph_data[module_key].itervalues())
    cause_fractions = [x/case_count for x in csmf_graph_data[module_key].values()]

    graph_title = module_key + ' CSMF'

    max_value = 1
    xlocations = np.arange(len(cause_keys))    # the x locations for the groups

    bar_width = .75 # the width of the bars

    # interactive mode off
    plt.ioff()
    fig, ax = plt.subplots()

    ax.set_title(graph_title)
    ax.set_ylabel('mortality fractions')
    ax.yaxis.grid()

    ax.set_xticklabels(cause_keys,rotation=90)
    ax.set_xticks(xlocations)

    ax.bar(xlocations, cause_fractions, bar_width, color='#C44440',align='center')

    #add whitespace at top of bar
    ax.set_ylim(top=max_value)

    #add whitespace before first bar and after last
    plt.xlim([min(xlocations) - .5, max(xlocations) + 1.0])

    #add some spacing for rotated xlabels
    plt.subplots_adjust(bottom=0.35)

    plt.savefig(output_dir + os.sep + graph_title +' graph.png',dpi=150)

    # clear the current figure
    plt.clf()

    # plt.close() causes a crash in os x.
    if sys.platform == 'darwin':
        del fig # cleans up the memory
    else:
        plt.close()


# labels for dict
global module_labels
global age_labels
global gender_labels
module_labels = ('adult','child','neonate')
age_labels = ('0-28 days', '29 days - 1 year', '1-4 years', '5-11 years', '12-19 years', '20-44 years', '45-59 years', '60+ years', 'unknown')
gender_labels = ('male','female', 'unknown')

# build ordered dict for values to be graphed. indexed by cause, the gender, then age.
global cause_graph_data
global csmf_graph_data
cause_graph_data = defaultdict(get_default_cause_dict)
csmf_graph_data = get_default_csmf_dict()

class Grapher():

    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.want_abort = 0


    def run(self):

        csmf_graph_data_unsorted = get_default_csmf_dict()

        for module_key in module_labels:

            # read and process data from csv. rU gives universal newline support
            # TODO what happens if you don't have a module
            try:
                csv_file = csv.DictReader(open(self.inputFilePath.replace('$module-tariff-causes.csv',module_key+'-tariff-causes.csv'),'rU'))

                updatestr = 'Making graphs for ' + module_key + '\n'
                wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

                for row in csv_file:
                    if self.want_abort == 1:
                        return

                    age_key = get_age_key(module_key,float(row['age']))
                    gender_key = get_gender_key(int(row['sex']))
                    cause_key = row['cause']

                    cause_graph_data[cause_key][gender_key][age_key] += 1
                    cause_graph_data['all'][gender_key][age_key] += 1

                    if cause_key in csmf_graph_data_unsorted[module_key]:
                        csmf_graph_data_unsorted[module_key][cause_key] += 1.0
                    else:
                        csmf_graph_data_unsorted[module_key].setdefault(cause_key,0.0)

            except IOError:
                print module_key+'-tariff-causes.csv not found'

            # sort csmf by value and make csmf graphs
            csmf_graph_data[module_key] = OrderedDict(sorted(csmf_graph_data_unsorted[module_key].iteritems(), key=lambda x: x[1]))
            make_csmf_graph(module_key,self.output_dir)

        # make cause of death graphs
        for cause_key in cause_graph_data.keys():
            make_cause_graph(cause_key,self.output_dir)

        updatestr = 'Finished making graphs\n'
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
    
    def abort(self):
        self.want_abort = 1