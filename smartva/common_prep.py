import re

from smartva.data.common_data import (
    ADDITIONAL_HEADERS,
    SHORT_FORM_ADDITIONAL_HEADERS_DATA,
    BINARY_CONVERSION_MAP,
    AGE_VARS,
    ADULT_RASH_DATA,
    CHILD_WEIGHT_CONVERSION_DATA,
    FREE_TEXT_VARS,
    WORD_SUBS,
    ADULT, CHILD, NEONATE,
)
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.loggers.application import warning_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import additional_headers_and_values

INPUT_FILENAME_TEMPLATE = 'cleanheaders.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-prepped.csv'


def int_value(x):
    try:
        return int(x)
    except ValueError:
        return 0


class CommonPrep(DataPrep):
    """
    This file cleans up input and converts from ODK collected data to VA variables.
    """

    def __init__(self, working_dir_path, short_form):
        super(CommonPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self._matrix_data = {
            ADULT: [],
            CHILD: [],
            NEONATE: []
        }

    def run(self):
        """
        Perform initial processing step for preparing input data.

        :return: True if processing was successful, False if aborted.
        :rtype : bool
        """
        super(CommonPrep, self).run()

        status_logger.info('Initial data prep')
        status_notifier.update({'progress': 1})

        headers, matrix = DataPrep.read_input_file(self.input_file_path())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        # Extend the headers with additional headers and read the remaining data into the matrix
        additional_data = {k: '' for k in ADDITIONAL_HEADERS}
        if self.short_form:
            additional_data.update(SHORT_FORM_ADDITIONAL_HEADERS_DATA)
        additional_headers, additional_values = additional_headers_and_values(headers, additional_data.items())

        headers.extend(additional_headers)

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(zip(additional_headers, additional_values)))

            self.convert_cell_to_int(row, AGE_VARS.values())

            self.process_binary_vars(row, BINARY_CONVERSION_MAP.items())

            self.convert_rash_data(row, ADULT_RASH_DATA)

            self.convert_weight_data(row, CHILD_WEIGHT_CONVERSION_DATA)

            self.convert_free_text(row, FREE_TEXT_VARS, WORD_SUBS)

            self.save_row(row)

        status_notifier.update({'sub_progress': None})

        self.write_data(headers, self._matrix_data)

        return bool(self._matrix_data[ADULT]), bool(self._matrix_data[CHILD]), bool(self._matrix_data[NEONATE])

    @staticmethod
    def convert_cell_to_int(row, conversion_data):
        """
        Convert specified cells to int value or 0 if cell is empty.

        :param row: Data from a single report.
        :param conversion_data: Headers of cells to convert.
        """
        # TODO: Eliminate this step in favor more robust future cell processing.
        for header in conversion_data:
            row[header] = int_value(row[header])

    @staticmethod
    def convert_rash_data(row, conversion_data):
        """
        Convert rash data into variables based on multiple choice questions.

        :param row: Data from a single report.
        :param conversion_data: Data structure with header and rash specific variable mapping.
        """
        for variable, mapping in conversion_data.items():
            try:
                rash_values = map(int, row[variable].split(' '))
            except ValueError:
                # No rash data. Continue.
                continue
            except KeyError as e:
                # Variable does not exist.
                warning_logger.debug('SID: {} variable \'{}\' does not exist. convert_rash_data'
                                     .format(row['sid'], e.message))
                continue
            else:
                if set(mapping['list']).issubset(set(rash_values)):
                    # if 1, 2, and 3 are selected, then change the value to 4 (all)
                    rash_values = [mapping['value']]
                # set adult rash to the other selected values
                for rash_index in range(min(len(rash_values), len(mapping['headers']))):
                    row[mapping['headers'][rash_index]] = rash_values[rash_index]

    @staticmethod
    def convert_weight_data(row, conversion_data):
        """
        Convert weights from kg to g.

        :param row: Data from a single report.
        :param conversion_data: Data structure with header and weight variable mapping.
        """
        for variable, mapping in conversion_data.items():
            try:
                units = int(row[variable])
            except ValueError:
                # No weight data. Skip.
                pass
            else:
                if units == 2:
                    weight = float(row[mapping[units]]) * 1000
                    row[variable] = 1
                    row[mapping[1]] = int(weight)

    @staticmethod
    def convert_free_text(row, free_text_vars, word_subs):
        """
        Substitute words in the word subs list (mostly misspellings, etc..)

        :param row: Data from a single report.
        :param free_text_vars: List of headers to process.
        :param word_subs: Dictionary of substitution words.
        """
        # warning_logger.debug('Free text column "{}" does not exist.'.format(question))
        for variable in free_text_vars:
            # check to see if any of the keys exist in the free text (keys can be multiple words like 'dog bite')
            new_answer_array = []
            for word in re.sub('[^a-z ]', '', row[variable].lower()).split(' '):
                if word in word_subs:
                    new_answer_array.append(WORD_SUBS[word])
                elif word:
                    new_answer_array.append(word)

            row[variable] = ' '.join(new_answer_array)

    @staticmethod
    def get_age_data(row):
        """
        Return age data in years, months, days, and module type.

        :param row: Data from a single report.
        :return: Age data in years, months, days, and module type.
        :rtype : dict
        """
        age_data = {}
        for age_group, variable in AGE_VARS.items():
            age_data[age_group] = int(row[variable])

        return age_data

    @staticmethod
    def get_matrix(matrix_data, years=0, months=0, days=0, module=0):
        """
        Returns the appropriate age range matrix for extending.

        Adult = 12 years or older
        Child = 29 days to 12 years
        Neonate = 28 days or younger
        Module is used if age data are not used.

        :param matrix_data: Dictionary of age range matrices.
        :param years: Age in years
        :param months: Age in months
        :param days: Age in days
        :param module: Module, if specified
        :return: Specific age range matrix.
        :rtype : list
        """
        if years >= 12 or (not years and not months and not days and module == 3):
            return matrix_data[ADULT]
        if years or months or days >= 29 or (not years and not months and not days and module == 2):
            return matrix_data[CHILD]
        return matrix_data[NEONATE]

    def save_row(self, row):
        """
        Save row of data in appropriate age matrix.

        :param row: Data from a single report.
        """
        self.get_matrix(self._matrix_data, **self.get_age_data(row)).extend([row])

    def write_data(self, headers, matrix_data):
        """
        Write intermediate prepped csv files.

        :param headers: Data headers.
        :param matrix_data: Data from a all reports.
        """
        status_logger.debug('Writing adult, child, neonate prepped.csv files')

        for age, matrix in matrix_data.items():
            if matrix:
                DataPrep.write_output_file(headers, matrix, self.output_file_path(age))
