import abc

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier

INPUT_FILENAME_TEMPLATE = '{:s}-symptom.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-symptom-rules.csv'


class RulesPrep(DataPrep):
    __metaclass__ = abc.ABCMeta

    def __init__(self, working_dir_path, short_form):
        super(RulesPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self.AGE_GROUP = 'None'

    def run(self):
        super(RulesPrep, self).run()

        status_logger.info('{} :: Processing rules data'.format(self.AGE_GROUP))
        status_notifier.update({'progress': 1})

