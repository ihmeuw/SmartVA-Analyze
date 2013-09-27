#!/opt/virtualenvs/ihme-va/bin/pythonw

import os
import wx
from threading import *
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
import csmfgraphs

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
    def __init__(self, notify_window, input_file, hce, output_dir, freetext, malaria):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.inputFilePath = input_file
        self.data = None
        self.hce = hce
        self.output_dir = output_dir
        self.freetext = freetext
        self.warningfile = open(self.output_dir + os.sep + 'warnings.txt', 'w')
        self.malaria = malaria
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        
        #set up the function calls
        self.cleanheaders = headers.Headers(self._notify_window, self.inputFilePath, self.output_dir)
        self.prep = vaprep.VaPrep(self._notify_window, self.output_dir + os.sep + "cleanheaders.csv", self.output_dir, self.warningfile)
        self.adultpresym = adultpresymptom.PreSymptomPrep(self._notify_window, self.output_dir + os.sep + "adult-prepped.csv", self.output_dir, self.warningfile)
        self.adultsym = adultsymptom.AdultSymptomPrep(self._notify_window, self.output_dir + os.sep + "adult-presymptom.csv", self.output_dir)
        self.adultresults = adulttariff.Tariff(self._notify_window, self.output_dir + os.sep + "adult-symptom.csv", self.output_dir, self.hce, self.freetext, self.malaria)
        self.childpresym = childpresymptom.PreSymptomPrep(self._notify_window, self.output_dir + os.sep + "child-prepped.csv", self.output_dir, self.warningfile)
        self.childsym = childsymptom.ChildSymptomPrep(self._notify_window, self.output_dir + os.sep + "child-presymptom.csv", self.output_dir)
        self.childresults = childtariff.Tariff(self._notify_window, self.output_dir + os.sep + "child-symptom.csv", self.output_dir, self.hce, self.freetext, self.malaria)
        self.neonatepresym = neonatepresymptom.PreSymptomPrep(self._notify_window, self.output_dir + os.sep + "neonate-prepped.csv", self.output_dir, self.warningfile)
        self.neonatesym = neonatesymptom.NeonateSymptomPrep(self._notify_window, self.output_dir + os.sep + "neonate-presymptom.csv", self.output_dir)
        self.neonateresults = neonatetariff.Tariff(self._notify_window, self.output_dir + os.sep + "neonate-symptom.csv", self.output_dir, self.hce, self.freetext)
        self.causegraph = causegraphs.CauseGraphs(self._notify_window, self.output_dir + os.sep + '$module-tariff-causes.csv', self.output_dir)
        #self.csmfgraph = csmfgraphs.CSMFGraphs(self._notify_window, self.output_dir + os.sep + '$module-tariff-causes.csv', self.output_dir)
        self.start()

    def run(self):
        #makes cleanheaders.csv
        self.cleanheaders.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #makes adult-prepped.csv, child-prepped.csv, neonate-prepped.csv
        self.prep.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # #makes adult-presymptom.csv
        self.adultpresym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return
        #
        # #makes adult-symptom.csv
        self.adultsym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return
        #
        # #creates adult output files
        self.adultresults.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return
               
        #makes child-presymptom.csv
        self.childpresym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #makes child-symptom.csv
        self.childsym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #creates child output files
        self.childresults.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #makes neonate-presymptom.csv  TODO:  right now this is the same as child presymptom, should probably just combine into one
        self.neonatepresym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #makes neonate-symptom.csv
        self.neonatesym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #creates neonate output files
        self.neonateresults.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #generate all cause graphs
        self.causegraph.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

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
    	#status.set('Done. Results are written to results.csv')
    	return

    def abort(self):
        """abort worker thread."""
        #Method for use by main thread to signal an abort
        self._want_abort = 1
        self.cleanheaders.abort()
        self.prep.abort()
        self.adultpresym.abort()
        self.adultsym.abort()
        self.adultresults.abort()
        self.childpresym.abort()
        self.childsym.abort()
        self.childresults.abort()
        self.neonatepresym.abort()
        self.neonatesym.abort()
        self.neonateresults.abort()
        self.causegraph.abort()
        if self.data:
            #print "trying to cancel"
            self.data.setCancelled();
        #else:
            #print "no data"
            #wx.PostEvent(self._notify_window, ResultEvent(None))
            