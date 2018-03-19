import re

from smartva.data.common_data import (
    CONSENT_HEADER,
    ADDITIONAL_HEADERS,
    SHORT_FORM_ADDITIONAL_HEADERS_DATA,
    BINARY_CONVERSION_MAP,
    AGE_VARS,
    RASH_DATA,
    WEIGHT_CONVERSION_DATA,
    FREE_TEXT_VARS,
    WORD_SUBS,
    ADULT, CHILD, NEONATE,
)
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
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
    """This file cleans up input and converts from ODK collected data to VA variables."""

    def __init__(self, working_dir_path, short_form):
        super(CommonPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self._matrix_data = {
            ADULT: [],
            CHILD: [],
            NEONATE: [],
            'invalid-age': [],
        }

    def run(self):
        """Perform initial processing step for preparing input data.

        Returns:
            tuple(bool): Tuple of bool values if VAs are present for Adult, Child, and Neonate.
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

            if not self.check_consent(row, CONSENT_HEADER):
                warning_logger.info('SID: {} Refused consent.'.format(row['sid']))
                continue

            self.expand_row(row, dict(zip(additional_headers, additional_values)))

            self.correct_missing_age(row)

            try:
                self.convert_cell_to_int(row, AGE_VARS.values())
            except KeyError as e:
                warning_logger.error('Missing age variable: {}'.format(e.message))
                missing_vars = [var for var in AGE_VARS.values() if var not in headers]
                status_logger.info('Cannot process data without: {}'.format(', '.join(missing_vars)))
                status_notifier.update('abort')
                continue

            self.process_binary_vars(row, BINARY_CONVERSION_MAP.items())

            self.convert_rash_data(row, RASH_DATA)

            self.convert_weight_data(row, WEIGHT_CONVERSION_DATA)

            self.convert_free_text(row, FREE_TEXT_VARS, WORD_SUBS)

            self.save_row(row)

        status_notifier.update({'sub_progress': None})

        self.write_data(headers, self._matrix_data)

        return bool(self._matrix_data[ADULT]), bool(self._matrix_data[CHILD]), bool(self._matrix_data[NEONATE])

    def check_consent(self, row, header):
        """Check consent. Consent is considered given if value is '1' or '' or the column is missing.
        A warning is logged if the value is invalid.

        Args:
            row (dict): Row of VA data.
            header (str): Consent column header name.

        Returns:
            bool:
        """
        try:
            if row[header] in ['', '1', 1]:
                return True
        except KeyError:
            return True
        warning_logger.info('SID: {} Invalid value for consent: {}'.format(row['sid'], row[header]))
        return False

    def correct_missing_age(self, row):
        """Ensure that the age group variable is set to missing if all AGE_VARS are blank"""
        if all([row.get(var, '') == '' for var in AGE_VARS.values()]):
            row[AGE_VARS['module']] = '9'  # Don't Know

    def convert_cell_to_int(self, row, conversion_data):
        """Convert specified cells to int value or 0 if cell is empty.

        Conversion data format:
            [quoted list of variable names]

        Args:
            row (dict): Row of VA data.
            conversion_data (list): Variable names of cells to convert.
        """
        # TODO: Eliminate this step in favor more robust future cell processing.
        for header in conversion_data:
            row[header] = int_value(row[header])

    def convert_rash_data(self, row, conversion_data):
        """Specialized method to convert rash data into variables based on multiple choice questions.
        Split and store values from a space delimited list of integers in intermediate variables.
        If the three locations [1 (face), 2 (trunk), 3 (extremities)] values are specified, change answer to 4 (Everywhere).

        Conversion data format:
            {
                '#read_var': {
                    'vars': [quoted list of write vars],
                    'locations': [list of location values],
                    'everywhere': 4
                }
            }

        Args:
            row (dict): Row of VA data.
            conversion_data (dict): Data structure with header and rash specific variable mapping.
        """
        for variable, mapping in conversion_data.items():
            try:
                rash_values = set(map(int, row[variable].split(' ')))
            except ValueError:
                # No rash data. Continue.
                continue
            except KeyError as e:
                # Variable does not exist.
                warning_logger.debug('SID: {} variable \'{}\' does not exist. convert_rash_data'
                                     .format(row['sid'], e.message))
                continue
            else:
                locations = set(mapping['locations'])
                if mapping['everywhere'] in rash_values or locations & rash_values == locations:
                    # if all locations are selected, then change the value to 'everywhere'
                    rash_values = {mapping['everywhere']}
                else:
                    # remove any illegal values
                    rash_values = locations & rash_values

                # set adult rash to the other selected values
                for index, value in enumerate(rash_values):
                    row[mapping['vars'][index]] = value

    def convert_weight_data(self, row, conversion_data):
        """Convert weights from kg to g.

        Conversion data format:
            {
                'units var': {
                    1: 'grams var',
                    2: 'kilograms var'
                },
            }

        Args:
            row (dict): Row of VA data.
            conversion_data (dict): Data structure with header and weight variable mapping.
        """
        for variable, mapping in conversion_data.items():
            try:
                units = int(row[variable])
            except ValueError:
                # No weight data. Skip.
                continue
            except KeyError:
                # Variable does not exist.
                continue
            else:
                if units == 2:
                    weight = float(row[mapping[units]]) * 1000
                    row[variable] = 1
                    row[mapping[1]] = int(weight)

    def convert_free_text(self, row, free_text_vars, word_subs):
        """Substitute words in the word subs list (mostly misspellings, etc..)

        Args:
            row (dict): Row of VA data.
            free_text_vars (list): Variables to process.
            word_subs (dict): Dictionary of substitution words.
        """
        # warning_logger.debug('Free text column "{}" does not exist.'.format(question))
        for variable in free_text_vars:
            # check to see if any of the keys exist in the free text (keys can be multiple words like 'dog bite')
            if variable in row:
                new_answer_array = []
                for word in re.sub('[^a-z ]', '', row[variable].lower()).split(' '):
                    if word:
                        new_answer_array.append(word_subs.get(word, word))

                row[variable] = ' '.join(new_answer_array)

    def get_age_data(self, row):
        """Return age data in years, months, days, and module type.

        Args:
            row (dict): Row of VA data.

        Returns:
            dict: Age data in years, months, days, and module type.
        """
        age_data = {}
        for age_group, variable in AGE_VARS.items():
            age_data[age_group] = int(row[variable])

        age_data.update({'sid': row['sid']})
        return age_data

    def get_matrix(self, matrix_data, years=0, months=0, days=0, module=0, sid=''):
        """Returns the appropriate age range matrix for extending.

        All four age variables are pre-processed and filled with a default
        value of zero before this method is called.

        Adult = 12 years or older
        Child = 29 days to 12 years
        Neonate = 28 days or younger
        Module is used if age data are not used.

        Args:
            matrix_data (dict): Dictionary of age range matrices.
            years (int): Age in years.
            months (int): Age in months.
            days (int): Age in days.
            module (int): Module, if specified.
            sid (str): row ID for logger

        Returns:
            list: Specific age range matrix.
        """
        # If there is age data (there is a sum) use it even if the module is
        # marked as "Refuesd" or "Don't Know"
        if sum([years, months, days]) == 0 and module in {8, 9}:
            warning_logger.warning('SID: {} does not have valid age data and is being removed from the analysis.'
                                     .format(sid))
            return matrix_data['invalid-age']
        if years >= 12 or (not years and not months and not days and module == 3):
            return matrix_data[ADULT]
        if years or months or days >= 29 or (not years and not months and not days and module == 2):
            return matrix_data[CHILD]
        return matrix_data[NEONATE]

    def save_row(self, row):
        """Save row of data in appropriate age matrix.

        Args:
            row (dict): Row of VA data.
        """
        self.get_matrix(self._matrix_data, **self.get_age_data(row)).extend([row])

    def write_data(self, headers, matrix_data):
        """Write intermediate prepped csv files.

        Args:
            headers (list): Data headers.
            matrix_data (dict): Data from a all reports.
        """
        status_logger.debug('Writing adult, child, neonate prepped.csv files')

        for age, matrix in matrix_data.items():
            if matrix:
                DataPrep.write_output_file(headers, matrix, self.output_file_path(age))
