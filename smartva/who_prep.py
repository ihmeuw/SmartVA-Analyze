from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.data import who_data

# Hackishly overwrite input to CommonPrep if necessary
INPUT_FILENAME_TEMPLATE = 'cleanheaders.csv'
OUTPUT_FILENAME_TEMPLATE = 'cleanheaders.csv'


class WHOPrep(DataPrep):

    def __init__(self, working_dir_path):
        super(WHOPrep, self).__init__(working_dir_path, True)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self.data_module = who_data

    def run(self):
        super(WHOPrep, self).run()

        status_logger.info('Mapping WHO Questionnaire')
        status_notifier.update({'progress': 1})

        _, matrix = DataPrep.read_input_file(self.input_file_path())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

        status_notifier.update({'sub_progress': None})

        DataPrep.write_output_file(self.data_module.EXPECTED_HEADERS, matrix,
                                   self.output_file_path(None))

