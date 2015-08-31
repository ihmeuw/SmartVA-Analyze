import csv

from smartva.loggers import status_logger


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

        status_logger.info('Checking form')

        first = True
        for row in reader:
            if first:
                for column in row:
                    if (column.find("adult_7_11") != -1):
                        status_logger.info('Detected SHORT form')

                        return True
                first = False
            else:
                status_logger.info('Detected standard form')
                return False

    def abort(self):
        self.want_abort = 1
