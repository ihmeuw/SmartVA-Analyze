#!/opt/virtualenvs/ihme-va/bin/pythonw

import csv
import string
import wx
import workerthread
import os

# Thread class that executes processing
class ShortFormTest():
    """Worker Thread Class."""
    def __init__(self, notify_window, input_file):
        self._notify_window = notify_window
        self.inputFilePath = input_file
    
    def run(self):
        reader = csv.reader(open( self.inputFilePath, 'Ub'))
        
        updatestr = "Checking form\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

        first = True
        for row in reader:
            if first:
                for column in row:
                    if (column.find("adult_7_11") != -1):
                        updatestr = "Detected SHORT form\n"
                        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

                        return True
                first = False
            else:
                updatestr = "Detected standard form\n"
                wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))
                return False

    	
    def abort(self):
        self.want_abort = 1