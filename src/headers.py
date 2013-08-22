#!/opt/virtualenvs/ihme-va/bin/pythonw

import csv
import string
import wx
import workerthread
import os

# Thread class that executes processing
class Headers():
    """Worker Thread Class."""
    def __init__(self, notify_window, input_file, output_dir):
        self._notify_window = notify_window
        self.inputFilePath = input_file
        self.output_dir = output_dir

    def run(self):
        # read stocks data, print status messages
        reader = csv.reader(open( self.inputFilePath, 'Ub'))
        writer = csv.writer(open(self.output_dir + os.sep + 'cleanheaders.csv', 'wb', buffering=0))
        
        updatestr = "Cleaning column headers\n"
        wx.PostEvent(self._notify_window, workerthread.ResultEvent(updatestr))

        first = 1
        for row in reader:
            newrow = list()
            if (first == 1):
                first = 2
                for col in row:
                    newcolname = ""
                    try:
                        lastindex = string.rindex(col, "-")
                        newcolname = col[lastindex+1:]
                    except ValueError:
                        newcolname = col
                    newrow.append(newcolname)

                writer.writerow(newrow)
            else:
                writer.writerow(row)
#            print '%s is %s (%s%%)' % (name, status, pct)

        # write stocks data as comma-separated values
        # writer.writerows([
        # ('GOOG', 'Google, Inc.', 505.24, 0.47, 0.09),
        # ('YHOO', 'Yahoo! Inc.', 27.38, 0.33, 1.22),
        # ('CNET', 'CNET Networks, Inc.', 8.62, -0.13, -1.49)
        # ])

        return 1
    	#print "done" 
    	#status.set('Done. Results are written to results.csv')