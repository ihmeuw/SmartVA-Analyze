#!/opt/virtualenvs/ihme-va/bin/pythonw

import os
import wx
from threading import *
from time import gmtime, strftime
import headers
import vaprep
import adultpresymptom
import adultsymptom
import adulttariff
import childpresymptom
import childsymptom
import childtariff
import neonatepresymptom
import neonatesymptom
import neonatetariff
import causegraphs

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
    def __init__(self, notify_window, input_file, hce, output_dir):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.inputFilePath = input_file
        self.data = None
        self.hce = hce
        self.output_dir = output_dir
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):

        #makes cleanheaders.csv
        cleanheaders = headers.Headers(self._notify_window, self.inputFilePath, self.output_dir)
        cleanheaders.run()

        #makes adult-prepped.csv, child-prepped.csv, neonate-prepped.csv
        prep = vaprep.VaPrep(self._notify_window, self.output_dir + os.sep + "cleanheaders.csv", self.output_dir)
        prep.run()
        
        # #makes adult-presymptom.csv
        adultpresym = adultpresymptom.PreSymptomPrep(self._notify_window, self.output_dir + os.sep + "adult-prepped.csv", self.output_dir)
        adultpresym.run()
        # 
        # #makes adult-symptom.csv
        adultsym = adultsymptom.AdultSymptomPrep(self._notify_window, self.output_dir + os.sep + "adult-presymptom.csv", self.output_dir)
        adultsym.run()
        # 
        # #creates adult output files
        adultresults = adulttariff.Tariff(self._notify_window, self.output_dir + os.sep + "adult-symptom.csv", self.output_dir)
        adultresults.run()
        # 
        #makes child-presymptom.csv
        childpresym = childpresymptom.PreSymptomPrep(self._notify_window, self.output_dir + os.sep + "child-prepped.csv", self.output_dir)
        childpresym.run()
        
        #makes child-symptom.csv
        childsym = childsymptom.ChildSymptomPrep(self._notify_window, self.output_dir + os.sep + "child-presymptom.csv", self.output_dir)
        childsym.run()
        
        #creates child output files
        childresults = childtariff.Tariff(self._notify_window, self.output_dir + os.sep + "child-symptom.csv", self.output_dir)
        childresults.run()
        
        #makes neonate-presymptom.csv  TODO:  right now this is the same as child presymptom, should probably just combine into one
        neonatepresym = neonatepresymptom.PreSymptomPrep(self._notify_window, self.output_dir + os.sep + "neonate-prepped.csv", self.output_dir)
        neonatepresym.run()
       
        #makes neonate-symptom.csv
        neonatesym = neonatesymptom.NeonateSymptomPrep(self._notify_window, self.output_dir + os.sep + "neonate-presymptom.csv", self.output_dir)
        neonatesym.run()
        
        #creates neonate output files
        neonateresults = neonatetariff.Tariff(self._notify_window, self.output_dir + os.sep + "neonate-symptom.csv", self.output_dir)
        neonateresults.run()
        
        # makes cause graphs
        # causegraph = causegraphs.CauseGraphs(self._notify_window, self.output_dir + os.sep + "neonate-tariff-causes.csv", self.output_dir)
        #         causegraph.run()
        
        # filename = ''
        #         validated = False
        #         if self.module is "Adult":
        #             filename = "Adult_available_symptoms.csv"
        #         elif self.module is "Child":
        #             filename = "Child_available_symptoms.csv"
        #         elif self.module is "Neonate":
        #             filename = "Neonate_available_symptoms.csv"


        
        # self.data = pyvaPackage.Data(notify_window=self._notify_window, module=self.module, input_filename=self.inputFilePath, available_filename=filename, HCE=self.hce)
        #         if (self._want_abort):
        #             wx.PostEvent(self._notify_window, ResultEvent(None))
        #             return
        #         score_matrix = self.data.calc_rf_scores(notify_window=self._notify_window)
        #         if (self._want_abort):
        #             wx.PostEventent(self._notify_window, ResultEvent(None))
        #             return
        #         prediction = self.data.rank_against_train_prediction(score_matrix)
        #         if (self._want_abort):
        #             wx.PostEvent(self._notify_window, ResultEvent(None))
        #             return
        #         self.data.save_scores(self.output_dir + '/results %s.csv'%strftime("%Y-%m-%d %H-%M-%S", gmtime()), prediction, score_matrix)

        wx.PostEvent(self._notify_window, ResultEvent("Done"))
    	#print "done" 
    	#status.set('Done. Results are written to results.csv')

    def abort(self):
        """abort worker thread."""
        #Method for use by main thread to signal an abort
        self._want_abort = 1
        if self.data:
            #print "trying to cancel"
            self.data.setCancelled();
        #else:
            #print "no data"
            #wx.PostEvent(self._notify_window, ResultEvent(None))
            