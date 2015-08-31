import csv
import wx

import workerthread


class ShortFormTest(object):
    """
    Check headers to determine if the short form is used.
    """

    def __init__(self, notify_window, input_file):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.want_abort = 0

    def run(self):
        reader = csv.reader(open(self.inputFilePath, 'Ub'))

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
