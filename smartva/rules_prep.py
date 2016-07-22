import abc

import smartva.data.common_data as common_data
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.rules import *

INPUT_FILENAME_TEMPLATE = '{:s}-presymptom.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-logic-rules.csv'

RULES_CAUSE_NUM_KEY = 'cause'

ADDITIONAL_DATA = {RULES_CAUSE_NUM_KEY: ''}


class RulesPrep(DataPrep):
    __metaclass__ = abc.ABCMeta

    def __init__(self, working_dir_path, short_form, age_group, rules):
        super(RulesPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self.AGE_GROUP = age_group

        self.rules = rules

    def run(self):
        super(RulesPrep, self).run()

        status_logger.info('{} :: Processing rules data'.format(self.AGE_GROUP))
        status_notifier.update({'progress': 1})

        headers, matrix = DataPrep.read_input_file(self.input_file_path())

        headers.extend(ADDITIONAL_DATA.keys())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, ADDITIONAL_DATA)

            self.pre_processing_step(row)

            for rule in self.rules:
                try:
                    if rule.logic_rule(row) is True:
                        row[RULES_CAUSE_NUM_KEY] = rule.CAUSE_ID
                        break
                except Exception as e:
                    warning_logger.warning('SID: {} rule `{}` failed complete: {}'.format(row['sid'], rule, e.message))

            self.post_processing_step(row)

        status_notifier.update({'sub_progress': None})

        DataPrep.write_output_file(headers, matrix, self.output_file_path())

        return True
