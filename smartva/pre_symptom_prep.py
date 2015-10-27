import re

from stemming.porter2 import stem

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import int_value_or_0

TIME_FACTORS = {
    1: 356.0,
    2: 30.0,
    3: 7.0,
    4: 1.0,
    5: 1 / 24.0,
    6: 1 / 1440.0
}


class PreSymptomPrep(DataPrep):
    FILENAME_TEMPLATE = '{:s}-presymptom.csv'

    def run(self):
        super(PreSymptomPrep, self).run()
        status_logger.info('{} :: Processing pre-symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

    @staticmethod
    def get_drop_index_list(headers, drop_pattern):
        """
        Find and return a list of header indices that match a given pattern.

        :param headers: List of headers.
        :param drop_pattern: Regular expression of drop pattern.
        :return: List of indices.
        """
        return [headers.index(header) for header in headers if re.match(drop_pattern, header)]

    @staticmethod
    def verify_answers_for_row(row, valid_range_data):
        """
        Verify answers in a row of data are valid.

        :param row: Row of data.
        :param valid_range_data: Dictionary of headers and valid ranges.
        :return: True if any values fail validation.
        """
        warnings = False
        for variable, range_list in valid_range_data.items():
            try:
                value = row[variable]
            except KeyError:
                pass  # Header not in data set.
            else:
                if value != '' and range_list:
                    try:
                        answer_array = value.split()
                    except AttributeError:
                        answer_array = [value]
                    for answer in answer_array:
                        if int(answer) not in range_list:
                            warning_logger.warning(
                                'SID: {} variable {} has an illegal value {}. Please see code book for legal values.'
                                .format(row['sid'], variable, value))
                            warnings = True
        return warnings

    @staticmethod
    def recode_answers(row, consolidation_map):
        """
        Consolidate answers from data answers into new variables.

        Consolidation map dictionary format:
            (read_header, write_header): {
                VAL: data_header
            }

        :param row: Row of data.
        :param consolidation_map: Dictionary of read/write variables and their data counterparts.
        """
        for data_headers, data_map in consolidation_map.items():
            read_header, write_header = data_headers
            try:
                value = int(row[read_header])
            except ValueError:
                # FIXME - This covers both the header index and the int operations.
                pass
            else:
                if value in data_map:
                    row[write_header] = row[data_map[value]]

    @staticmethod
    def calculate_duration_vars(row, duration_vars, special_case_vars):
        """
        Calculate duration variables in days.

        :param row: Row of data.
        :param duration_vars: List of variables containing duration variables.
        :param special_case_vars: Dictionary of special variables and their value if duration is blank.
        """
        for var in duration_vars:
            code_var, length_var = '{}a'.format(var), '{}b'.format(var)
            code_value = int_value_or_0(row[code_var])
            length_value = int_value_or_0(row[length_var])

            if var in special_case_vars and length_value == '':
                row[var] = special_case_vars[var]
            else:
                row[var] = TIME_FACTORS.get(code_value, 0) * length_value

    @staticmethod
    def convert_free_text_words(row, input_word_list, word_map):
        """
        Process free text word lists into binary variables.

        :param row: Row of data.
        :param input_word_list: List of free text words to process.
        :param word_map: Dictionary of words and variables.
        """
        for word in input_word_list:
            try:
                row[word_map[stem(word)]] = 1
                warning_logger.warning('Word {} map {}'.format(stem(word), word_map[stem(word)]))
            except KeyError:
                # Word is not in the data map.
                pass
            except ValueError:
                warning_logger.warning('SID: {} variable {} not found for valid word "{}".'
                                       .format(row['sid'], word_map[stem(word)], word))

    @staticmethod
    def convert_free_text_vars(row, data_headers, word_map):
        """
        Process all free text data from a list of data headers into binary variables.

        :param row: Row of data.
        :param data_headers: List of headers to process.
        :param word_map: Dictionary of words and variables.
        """
        for data_header in data_headers:
            if row[data_header]:
                word_list = row[data_header].split(' ')
                PreSymptomPrep.convert_free_text_words(row, word_list, word_map)

    @staticmethod
    def fill_missing_data(row, default_fill):
        """
        Fill missing data with default fill values.

        :param row: Row of data.
        :param default_fill: Dictionary of headers and default values.
        """
        for variable, value in row.items():
            if value == '':
                row[variable] = default_fill.get(variable, '')
