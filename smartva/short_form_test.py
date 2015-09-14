import csv

from smartva.loggers import warning_logger
from smartva.utils import status_notifier


class ShortFormTest(object):
    """
    Check headers to determine if the short form is used.
    """

    def __init__(self, input_file):
        self.inputFilePath = input_file
        self.want_abort = 0

    def run(self):
        status_notifier.update({'progress': (1,)})

        reader = csv.reader(open(self.inputFilePath, 'Ub'))

        if 'adult_7_11' in next(reader):
            warning_logger.debug('Detected standard form')
            return False

        warning_logger.debug('Detected short form')
        return True

    def abort(self):
        self.want_abort = 1
