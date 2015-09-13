import csv
import os

from smartva.loggers import status_logger
from smartva.utils import status_notifier


# Thread class that executes processing
class Headers(object):
    """
    TODO - Write good doc string.
    """

    def __init__(self, input_file, output_dir):
        self.inputFilePath = input_file
        self.output_dir = output_dir
        self.want_abort = 0

    def run(self):
        status_notifier.update({'progress': (2,)})

        reader = csv.reader(open(self.inputFilePath, 'Ub'))
        writer = csv.writer(open(self.output_dir + os.sep + 'cleanheaders.csv', 'wb', buffering=0))

        status_logger.info('Cleaning column headers')

        count = 0
        for count, row in enumerate(reader):
            if count == 0:
                new_row = []
                for col in row:
                    # Split the column name at each '-' and take the last item.
                    new_row.append(col.split('-')[-1])

                writer.writerow(new_row)
            else:
                writer.writerow(row)

        # if count is less than 1, we have no data to process
        if count < 1:
            status_logger.info('No data to process, stopping')
            return 0
        return 1

    def abort(self):
        self.want_abort = 1
