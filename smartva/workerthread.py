import os
import threading

import wx

from smartva import headers
from smartva import vaprep
from smartva import adultpresymptom
from smartva import adultsymptom
from smartva import adulttariff
from smartva import childpresymptom
from smartva import childsymptom
from smartva import childtariff
from smartva import neonatepresymptom
from smartva import neonatesymptom
from smartva import neonatetariff
from smartva import causegrapher
from smartva import csmfgrapher
from smartva import short_form_test

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
class WorkerThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window, input_file, hce, output_dir, freetext, malaria, country):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.inputFilePath = input_file
        self.data = None
        self.hce = hce
        self.output_dir = output_dir
        self.freetext = freetext
        self.warningfile = open(self.output_dir + os.sep + 'warnings.txt', 'w')
        self.malaria = malaria
        self.country = country
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this

        self.shortform = False

        self.start()

    def run(self):

        intermediate_dir = self.output_dir + os.sep + "intermediate-files"
        figures_dir = self.output_dir + os.sep + "figures"

        if not os.path.exists(intermediate_dir):
            os.mkdir(intermediate_dir)
        if not os.path.exists(figures_dir):
            os.mkdir(figures_dir)

        self.shortFormTest = short_form_test.ShortFormTest(self._notify_window, self.inputFilePath)
        self.shortform = self.shortFormTest.run()


        # TODO should only pass the file to these methods. you can figure out self.output_dir from the file
        # set up the function calls
        self.cleanheaders = headers.Headers(self.inputFilePath, intermediate_dir)
        self.prep = vaprep.VaPrep(intermediate_dir + os.sep + "cleanheaders.csv", intermediate_dir, self.warningfile, self.shortform)
        self.adultpresym = adultpresymptom.PreSymptomPrep(intermediate_dir + os.sep + "adult-prepped.csv", intermediate_dir, self.warningfile, self.shortform)
        self.adultsym = adultsymptom.AdultSymptomPrep(self._notify_window, intermediate_dir + os.sep + "adult-presymptom.csv", intermediate_dir, self.shortform)
        self.adultresults = adulttariff.Tariff(self._notify_window, intermediate_dir + os.sep + "adult-symptom.csv", self.output_dir, intermediate_dir, self.hce, self.freetext, self.malaria, self.country, self.shortform)
        self.childpresym = childpresymptom.PreSymptomPrep(self._notify_window, intermediate_dir + os.sep + "child-prepped.csv", intermediate_dir, self.warningfile, self.shortform)
        self.childsym = childsymptom.ChildSymptomPrep(self._notify_window, intermediate_dir + os.sep + "child-presymptom.csv", intermediate_dir, self.shortform)
        self.childresults = childtariff.Tariff(self._notify_window, intermediate_dir + os.sep + "child-symptom.csv", self.output_dir, intermediate_dir, self.hce, self.freetext, self.malaria, self.country, self.shortform)
        self.neonatepresym = neonatepresymptom.PreSymptomPrep(self._notify_window, intermediate_dir + os.sep + "neonate-prepped.csv", intermediate_dir, self.warningfile, self.shortform)
        self.neonatesym = neonatesymptom.NeonateSymptomPrep(self._notify_window, intermediate_dir + os.sep + "neonate-presymptom.csv", intermediate_dir)
        self.neonateresults = neonatetariff.Tariff(self._notify_window, intermediate_dir + os.sep + "neonate-symptom.csv", self.output_dir, intermediate_dir, self.hce, self.freetext, self.country, self.shortform)
        self.causegrapher = causegrapher.CauseGrapher(self._notify_window, self.output_dir + os.sep + '$module-predictions.csv', figures_dir)
        self.csmfgrapher = csmfgrapher.CSMFGrapher(self._notify_window, self.output_dir + os.sep + '$module-csmf.csv', figures_dir)

        # makes cleanheaders.csv
        hasdata = self.cleanheaders.run()
        if hasdata == 0 or self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes adult-prepped.csv, child-prepped.csv, neonate-prepped.csv
        # we have data at this point, so all of these files should have been created
        self.prep.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes adult-presymptom.csv
        adult_data = self.adultpresym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes adult-symptom.csv
        if adult_data == 1:
            self.adultsym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        #
        # creates adult output files
        if adult_data == 1:
            self.adultresults.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes child-presymptom.csv
        child_data = self.childpresym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes child-symptom.csv
        if child_data == 1:
            self.childsym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # creates child output files
        if child_data == 1:
            self.childresults.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes neonate-presymptom.csv
        # TODO:  right now this is the same as child presymptom, should probably just combine into one
        neonate_data = self.neonatepresym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # makes neonate-symptom.csv
        if neonate_data == 1:
            self.neonatesym.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # creates neonate output files
        if neonate_data == 1:
            self.neonateresults.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # generate all cause graphs
        self.causegrapher.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        # generate all csmf graphs
        self.csmfgrapher.run()
        if self._want_abort == 1:
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        wx.PostEvent(self._notify_window, ResultEvent("Done"))
        # status.set('Done. Results are written to results.csv')
        return

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
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
        self.causegrapher.abort()
        self.csmfgrapher.abort()
        if self.data:
            self.data.setCancelled()
