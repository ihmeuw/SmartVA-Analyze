#!/opt/virtualenvs/ihme-va/bin/pythonw

import os
import wx
from wx import *
import pyvaPackage
from threading import *
import neonate_validator
from time import gmtime, strftime

EVT_RESULT_ID = wx.NewId()
EVT_PROGRESS_ID = wx.NewId()
 
def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)
    
def EVT_PROGRESS(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_PROGRESS_ID, func)

    
class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        

class ProgressEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, progress=None, progressmax=None):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PROGRESS_ID)
        self.progress = progress
        self.progressmax = progressmax

# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, input_file, hce, module, output_dir):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.inputFilePath = input_file
        self.data = None
        self.hce = hce
        self.module = module
        self.output_dir = output_dir
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        #data = pyvaPackage.Data(update=self.addText, module="Neonate", input_filename=self.inputFilePath, available_filename="/Users/carlhartung/Desktop/SmartVA/Examples/Neonate_available_symptoms.csv", HCE="HCE")
        #score_matrix = data.calc_rf_scores(update=self.addText)
        
        filename = ''
        validated = False
        if self.module is "Adult":
            filename = "Adult_available_symptoms.csv"
        elif self.module is "Child":
            filename = "Child_available_symptoms.csv"
        elif self.module is "Neonate":
            filename = "Neonate_available_symptoms.csv"
            #validated = neonate_validator.validate(notify_window=self._notify_window, inputfile=self.inputFilePath)
            
        #if not validated:
            #return
        
        self.data = pyvaPackage.Data(notify_window=self._notify_window, module=self.module, input_filename=self.inputFilePath, available_filename=filename, HCE=self.hce)
        if (self._want_abort):
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return
        score_matrix = self.data.calc_rf_scores(notify_window=self._notify_window)
        prediction = self.data.rank_against_train_prediction(score_matrix)
        self.data.save_scores(self.output_dir + '/results %s.csv'%strftime("%Y-%m-%d %H-%M-%S", gmtime()), prediction, score_matrix)

        wx.PostEvent(self._notify_window, ResultEvent("Done"))
    	print "done" 
    	#status.set('Done. Results are written to results.csv')

    def abort(self):
        """abort worker thread."""
        #Method for use by main thread to signal an abort
        self._want_abort = 1
        if self.data:
            print "trying to cancel"
            self.data.setCancelled();
        else:
            print "no data"
            wx.PostEvent(self._notify_window, ResultEvent(None))
            