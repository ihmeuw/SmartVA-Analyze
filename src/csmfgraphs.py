#!/usr/bin/env python
import csv
import re
import sys
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import wx

import workerthread

# http://stackoverflow.com/questions/4126348/how-do-i-rewrite-this-function-to-implement-ordereddict/4127426#4127426
class OrderedDefaultDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)

    def __missing__ (self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = self.default_factory if self.default_factory else tuple()
        return type(self), args, None, None, self.items()


# make and save csfm graph
def make_csmf_graph(module_key, output_dir):

    graph_title = "CSMF"

    # TODO Adult vs Child vs Neonatal
    # TODO What is n?
    # TODO What is Percentage Indeterminate?
    cause_keys = graph_data.keys()
    cause_fractions = graph_data.values()

    ylocations = np.arange(len(cause_keys))

    plt.barh(ylocations, cause_fractions,color='#C44440')
    plt.yticks(ylocations, cause_keys)

    ## add whitespace before first bar and after last
    plt.ylim([min(ylocations) - 1.5, max(ylocations) + 1.5])

    plt.title(graph_title)
    plt.xlabel('Mortality fractions')

    plt.savefig(graph_title+' graph.png',dpi=150)

    # clear the current figure
    plt.clf()

    # plt.close() causes a crash in os x.
    if sys.platform == 'darwin':
        del plt # cleans up the memory
    else:
        plt.close()

# build ordered dict for values to be graphed. indexed by cause, the gender, then age. 
global graph_data
global module_labels
module_labels = ('adult','child','neonate')
graph_data = OrderedDefaultDict(float)

class CSMFGraph():

    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.want_abort = 0

    def run(self):

        for module_key in module_labels:

            # read and process data from csv. rU gives universal newline support
            csv_file = csv.DictReader(open(self.inputFilePath.replace('$module-tariff-causes.csv',module_key+'-tariff-causes.csv'),'rU'))

            updatestr = 'Making CSMF graphs for ' + module_key + '\n'
            wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

            for row in csv.DictReader(open(csv_file,'rU')):
                if self.want_abort == 1:
                    return
                cause_key = re.sub('[^\w\-_\. ]', '', row['decision1_gs_text34']).rstrip()
                cause_fraction = row['cause_fraction']
                # TODO are cause_fractions always floats?
                graph_data[cause_key] = float(cause_fraction)

            graph_data = OrderedDict(sorted(graph_data.iteritems(), key=lambda x: x[1]))
            #make_csmf_graph(module_key,self.output_dir)

            #   TODO; maybe
            # graph_data.clear();


        updatestr = 'Finished making CSMF graphs\n'
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

    def abort(self):
        self.want_abort = 1