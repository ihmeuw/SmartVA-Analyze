import csv

from smartva.loggers import status_logger
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

        status_logger.info('Checking form')

        if 'adult_7_11' in next(reader):
            status_logger.info('Detected standard form')
            return False

        status_logger.info('Detected SHORT form')
        return True

    def abort(self):
        self.want_abort = 1
