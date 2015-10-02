import csv
import os
import re

from stemming.porter2 import stem

from smartva.default_fill_data import ADULT_DEFAULT_FILL, ADULT_DEFAULT_FILL_SHORT
from smartva.answer_ranges import ADULT_RANGE_LIST
from smartva.presymptom_conversions import ADULT_HEADER_CONVERSION_MAP
from smartva.word_conversions import ADULT_WORDS_TO_VARS
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.adult_pre_symptom_data import (
    GENERATED_HEADERS_DATA,
    CONSOLIDATION_MAP,
    BINARY_CONVERSION_MAP,
    SHORT_FORM_FREE_TEXT_CONVERSION,
    FREE_TEXT_HEADERS,
    SKIP_PATTERN_DATA,
    TIME_FACTORS,
    DURATION_VARS,
    DURATION_VARS_SHORT_FORM_DROP_LIST,
    DURATION_VARS_SPECIAL_CASE
)
from smartva.conversion_utils import (
    ConversionError,
    int_value_or_0,
    additional_headers_and_values,
    convert_binary_variable,
    check_skip_patterns
)

FILENAME_TEMPLATE = '{:s}-presymptom.csv'
DROP_PATTERN = '[cpn]([_\d]|hild|omplications|rovider|eonate)'


class AdultPreSymptomPrep(object):
    AGE_GROUP = 'adult'

    def __init__(self, input_file, output_dir, short_form):
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.short_form = short_form

        self.want_abort = False
        self.warnings = False

    def run(self):
        status_notifier.update({'progress': (2,)})

        status_logger.info('Adult :: Processing pre-symptom data')

        if self.short_form:
            default_fill = ADULT_DEFAULT_FILL_SHORT
        else:
            default_fill = ADULT_DEFAULT_FILL

        matrix = []

        with open(self.input_file_path, 'rb') as f:
            reader = csv.reader(f)

            headers = next(reader)

            additional_headers_data = GENERATED_HEADERS_DATA + [(k, '') for k in DURATION_VARS]
            additional_headers, additional_values = additional_headers_and_values(headers, additional_headers_data)

            headers.extend(additional_headers)

            self.rename_odk_headers(headers, ADULT_HEADER_CONVERSION_MAP)

            drop_index_list = self.get_drop_index_list(headers, DROP_PATTERN)

            headers = self.drop_from_list(headers, drop_index_list)

            for row in reader:
                new_row = self.drop_from_list(row + additional_values, drop_index_list)
                matrix.append(new_row)

        # Make sure we have data, else just stop this module
        if not matrix:
            warning_logger.debug('Adult :: No data, skipping module')
            return False

        status_logger.debug('Adult :: Verifying answers fall within legal bounds')

        # calculations for the generated variables:
        # i.e. recode
        # do this before skip patterns so generated variables aren't 0
        for row in matrix:

            self.warnings = self.verify_answers_for_row(headers, row, ADULT_RANGE_LIST)

            self.convert_free_text_headers(headers, row, FREE_TEXT_HEADERS, ADULT_WORDS_TO_VARS)

            if self.short_form:
                word_list = [v for k, v in SHORT_FORM_FREE_TEXT_CONVERSION.items() if row[headers.index(k)] in [1, '1']]
                if word_list:
                    self.convert_free_text_words(headers, row, ADULT_WORDS_TO_VARS, word_list)

            # Consolidate answers
            for data_headers, data_map in CONSOLIDATION_MAP.items():
                read_header, write_header = data_headers
                try:
                    value = int(row[headers.index(read_header)])
                except ValueError:
                    # TODO - This covers both the header index and the int operations.
                    pass
                else:
                    if value in data_map:
                        row[headers.index(write_header)] = row[headers.index(data_map[value])]

            # Convert binary variables
            for data_header, data_map in BINARY_CONVERSION_MAP.items():
                try:
                    convert_binary_variable(headers, row, data_header, data_map)
                except ConversionError as e:
                    warning_logger.debug(e.message)

            self.warnings |= check_skip_patterns(headers, row, SKIP_PATTERN_DATA)

        for row in matrix:
            self.fill_missing_data(headers, row, default_fill)

        duration_vars = DURATION_VARS

        if self.short_form:
            for var in DURATION_VARS_SHORT_FORM_DROP_LIST:
                duration_vars.remove(var)

        for row in matrix:
            self.calculate_duration_variables(headers, row, duration_vars, DURATION_VARS_SPECIAL_CASE)

        drop_index_list = self.get_drop_index_list(headers, 'adult')
        drop_index_list += [headers.index('{}a'.format(header)) for header in DURATION_VARS]
        drop_index_list += [headers.index('{}b'.format(header)) for header in DURATION_VARS]
        drop_index_list += ['a4_02']

        headers = self.drop_from_list(headers, drop_index_list)
        for i, row in enumerate(matrix):
            matrix[i] = self.drop_from_list(row, drop_index_list)

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb', buffering=0) as f:
            adult_writer = csv.writer(f)

            adult_writer.writerow(headers)
            adult_writer.writerows(matrix)

        if not self.warnings:
            status_logger.debug('Adult :: Answers verified')
        else:
            status_logger.info('Adult :: Warnings found, please check warnings.txt')

        return True

    @staticmethod
    def fill_missing_data(headers, row, default_fill):
        for header, value in default_fill.items():
            if row[headers.index(header)] == '':
                row[headers.index(header)] = value

    @staticmethod
    def calculate_duration_variables(headers, row, duration_vars, special_case_vars):
        for var in duration_vars:
            code_var, length_var = '{}a'.format(var), '{}b'.format(var)
            code_value = int_value_or_0(row[headers.index(code_var)])
            length_value = int_value_or_0(row[headers.index(length_var)])

            if var in special_case_vars and not length_value:
                row[headers.index(var)] = special_case_vars[var]
            else:
                row[headers.index(var)] = TIME_FACTORS.get(code_value, 0) * length_value

    @staticmethod
    def drop_from_list(item_list, drop_index_list):
        return [item for index, item in enumerate(item_list) if index not in drop_index_list]

    @staticmethod
    def get_drop_index_list(headers, drop_pattern):
        return [headers.index(header) for header in headers if re.match(drop_pattern, header)]

    @staticmethod
    def rename_odk_headers(headers, conversion_map):
        for old_header, new_header in conversion_map.items():
            try:
                headers[headers.index(old_header)] = new_header
            except (KeyError, ValueError):
                pass  # Header did not exist.

    @staticmethod
    def verify_answers_for_row(headers, row, valid_range_data):
        # Verify answers
        warnings = False
        for header, range_list in valid_range_data.items():
            try:
                value = row[headers.index(header)]
            except ValueError:
                pass  # Header not in data set.
            else:
                if value != '' and range_list:
                    try:
                        answer_array = value.split()
                    except AttributeError:
                        answer_array = [value]
                    for answer in answer_array:
                        if int(answer) not in range_list:
                            warning_logger.warning('SID: {} variable {} has an illegal value {}. '
                                                   'Please see Codebook for legal values.'
                                                   .format(row[headers.index('sid')], header, value))
                            warnings = True
        return warnings

    def abort(self):
        self.want_abort = True

    @staticmethod
    def convert_free_text_headers(headers, row, data_headers, data_map):
        for data_header in data_headers:
            if row[headers.index(data_header)]:
                word_list = row[headers.index(data_header)].split(' ')
                AdultPreSymptomPrep.convert_free_text_words(headers, row, data_map, word_list)

    @staticmethod
    def convert_free_text_words(headers, row, data_map, word_list):
        for word in word_list:
            try:
                row[headers.index(data_map[stem(word)])] = 1
            except KeyError:
                # Word is not in the data map.
                pass
