import csv
import os
import string

from smartva.loggers import status_logger


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
        reader = csv.reader(open(self.inputFilePath, 'Ub'))
        writer = csv.writer(open(self.output_dir + os.sep + 'cleanheaders.csv', 'wb', buffering=0))

        status_logger.info('Cleaning column headers')

        count = 0
        for row in reader:
            count += 1
            newrow = list()
            if count == 1:
                for col in row:
                    try:
                        lastindex = string.rindex(col, '-')
                        newcolname = col[lastindex + 1:]
                    except ValueError:
                        newcolname = col
                    newrow.append(newcolname)

                writer.writerow(newrow)
            else:
                writer.writerow(row)

        # if count is less than 2, we have no data to process
        if count < 2:
            status_logger.info('No data to process, stopping')
            return 0
        return 1

    def abort(self):
        self.want_abort = 1
