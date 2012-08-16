#!/opt/virtualenvs/ihme-va/bin/pythonw

import os
import wx
from wx import *
import pyvaPackage
from threading import *

EVT_RESULT_ID = wx.NewId()
 
def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)
    
class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, input_file):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.inputFilePath = input_file
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        #data = pyvaPackage.Data(update=self.addText, module="Neonate", input_filename=self.inputFilePath, available_filename="/Users/carlhartung/Desktop/SmartVA/Examples/Neonate_available_symptoms.csv", HCE="HCE")
        #score_matrix = data.calc_rf_scores(update=self.addText)
        
        data = pyvaPackage.Data(notify_window=self._notify_window, module="Neonate", input_filename=self.inputFilePath, available_filename="/Users/carlhartung/Desktop/SmartVA/Examples/Neonate_available_symptoms.csv", HCE="HCE")
        score_matrix = data.calc_rf_scores(notify_window=self._notify_window)

    def abort(self):
        """abort worker thread."""
        #Method for use by main thread to signal an abort
        self._want_abort = 1
