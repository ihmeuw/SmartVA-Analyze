import copy
import csv
import os

from stemming.porter2 import stem

from smartva.default_fill_data import ADULT_DEFAULT_FILL, ADULT_DEFAULT_FILL_SHORT
from smartva.answer_ranges import adult_rangelist
from smartva.presymptom_conversions import adult_conversionVars
from smartva.word_conversions import ADULT_WORDS_TO_VARS
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.adult_pre_symptom_data import (
    GENERATED_HEADERS_DATA,
    CONSOLIDATION_MAP,
    BINARY_CONVERSION_MAP,
    SHORT_FORM_FREE_TEXT_CONVERSION,
    FREE_TEXT_HEADERS,
    SKIP_PATTERN_DATA
)
from smartva.conversion_utils import (
    ConversionError,
    additional_headers_and_values,
    convert_binary_variable
)

FILENAME_TEMPLATE = '{:s}-presymptom.csv'


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

            additional_headers, additional_values = additional_headers_and_values(headers, GENERATED_HEADERS_DATA)
            headers.extend(additional_headers)

            for row in reader:
                matrix.append(row + additional_values)

        # Make sure we have data, else just stop this module
        if not matrix:
            warning_logger.debug('Adult :: No data, skipping module')
            return False

        # TODO - Move this into 'common-prep' module. Also, this is a bit too magical. Do something about that.
        # drop all child variables
        headers_copy = copy.deepcopy(headers)
        for col in headers_copy:
            if col.startswith('c') or col.startswith('p'):
                index = headers.index(col)
                for row in matrix:
                    del row[index]
                headers.remove(col)

        # switch to new variables:
        for i, col in enumerate(headers):
            # only swap headers with values to swap
            try:
                swap = adult_conversionVars[col]
                headers[i] = swap
            except KeyError:
                pass  # noooooooop

        status_logger.debug('Adult :: Verifying answers fall within legal bounds')

        # calculations for the generated variables:
        # i.e. recode
        # do this before skip patterns so generated variables aren't 0
        for row in matrix:

            # Verify answers
            for i, col in enumerate(row):
                header = headers[i]
                if col != '':
                    # if it's empty, we just skip it.  not sure there's a "required"
                    range_test = adult_rangelist.get(header)
                    if not (range_test is None or range_test == ''):
                        try:
                            answer_array = col.split(' ')
                        except AttributeError:
                            answer_array = [col]
                        for answer in answer_array:
                            if int(answer) not in range_test:
                                # ERROR
                                warning_logger.warning('Adult :: Value {} is not legal for variable {}, please see Codebook for legal values'.format(col, header))
                                self.warnings = True

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

            # Check skip patterns
            i = 0
            for skip_pattern_item in SKIP_PATTERN_DATA:
                skip_header, skip_pattern_item_data = skip_pattern_item
                skip_condition_data, skip_list = skip_pattern_item_data
                skip_condition_answer, skip_condition_value = skip_condition_data
                try:
                    # Get cell value
                    skip_header_answer = row[headers.index(skip_header)]
                except ValueError:
                    # Header is not in list
                    pass
                else:
                    try:
                        # Try to convert cell value to integer
                        skip_header_answer = int(skip_header_answer)
                    except ValueError:
                        pass
                    if (skip_header_answer == skip_condition_answer) is not skip_condition_value:
                        for skip_list_item in skip_list:
                            skip_list_item_value = row[headers.index(skip_list_item)]
                            try:
                                skip_list_item_value = int(skip_list_item_value)
                            except ValueError:
                                pass
                            if bool(skip_list_item_value):
                                print('check {} {} {} {}'.format(row[5], skip_header, skip_list_item, skip_list_item_value))
                                row[headers.index(skip_list_item)] = default_fill[skip_list_item]


            # general vars

            g5_04a = row[headers.index('g5_04a')]
            if g5_04a is not None and g5_04a != '':
                g5_04a = int(g5_04a)
            else:
                g5_04a = 0
            if g5_04a < 12 or g5_04a == 999:
                g5_05 = row[headers.index('g5_05')]
                if not (g5_05 is None or g5_05 == ''):
                    self.print_warning('g5_05', i, row, headers, default_fill)
            if g5_04a < 5 or g5_04a == 999:
                g5_06a = row[headers.index('g5_06a')]
                if not (g5_06a is None or g5_06a == ''):
                    self.print_warning('g5_06a', i, row, headers, default_fill)

            # added for short form
            a4_01 = row[headers.index('a4_01')]
            a4_02_2 = row[headers.index('a4_02_2')]
            a4_02_3 = row[headers.index('a4_02_3')]
            a4_02_4 = row[headers.index('a4_02_4')]
            a4_02_5a = row[headers.index('a4_02_5a')]
            if a4_01 != '1' or (a4_02_2 != '1' and a4_02_3 != '1' and a4_02_4 != '1' and a4_02_5a != '1'):
                a4_03 = row[headers.index('a4_03')]
                if not (a4_03 is None or a4_03 == ''):
                    self.print_warning('a4_03', i, row, headers, default_fill)

        if not self.warnings:
            status_logger.debug('Adult :: Answers verified')
        else:
            status_logger.info('Adult :: Warnings found, please check warnings.txt')

        status_logger.debug('Adult :: Filling in default values for empty columns')
        # fill in missing default values:
        for row in matrix:
            for i, col in enumerate(row):
                header = headers[i]
                default = default_fill.get(header)
                if default is not None and col == '':
                    row[i] = default_fill[header]

        status_logger.debug('Adult :: Processing duration variables')
        # fix duration variables
        duration_vars = ['a2_01', 'a2_03', 'a2_08', 'a2_15', 'a2_22', 'a2_24', 'a2_26', 'a2_28', 'a2_33', 'a2_37',
                         'a2_41', 'a2_48', 'a2_54', 'a2_58', 'a2_62', 'a2_65', 'a2_68', 'a2_70', 'a2_73', 'a2_76',
                         'a2_79', 'a2_83', 'a2_86', 'a3_08', 'a3_11', 'a3_16', 'a5_04']

        # add duration variables
        for var in duration_vars:
            headers.append(var)
            for row in matrix:
                row.append('')

        for var in duration_vars:
            if var == 'a3_16' and self.short_form:
                continue
            a = var + 'a'
            b = var + 'b'
            a_index = headers.index(a)
            b_index = headers.index(b)
            index = headers.index(var)

            for row in matrix:
                value = row[b_index]
                v2 = row[a_index]

                if (value == '') and var == 'a5_04':
                    # special case for injuries
                    row[index] = '999'
                else:
                    if value == '':
                        row[index] = '0'
                    else:
                        row[index] = float(value)
                    if row[a_index] == '1':
                        row[index] = float(row[index]) * 365.0
                    if row[a_index] == '2':
                        row[index] = float(row[index]) * 30.0
                    if row[a_index] == '3':
                        row[index] = float(row[index]) * 7.0
                    if row[a_index] == '5':
                        row[index] = float(row[index]) / 24.0
                    if row[a_index] == '6':
                        row[index] = float(row[index]) / 1440.0

        # drop old a/b variables
        # we do two loops to make sure we don't cross indexes, inefficient...
        for var in duration_vars:
            a = var + 'a'
            b = var + 'b'
            a_index = headers.index(a)
            headers.remove(a)

            for row in matrix:
                del row[a_index]

            b_index = headers.index(b)
            headers.remove(b)
            for row in matrix:
                del row[b_index]

        dropme = headers.index('a4_02')
        headers.remove('a4_02')
        for row in matrix:
            del row[dropme]

        # get rid of all unused 'adult' headers
        headers_copy = copy.deepcopy(headers)
        for col in headers_copy:
            if col.startswith('adult'):
                index = headers.index(col)
                for row in matrix:
                    del row[index]
                headers.remove(col)

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb', buffering=0) as f:
            adultwriter = csv.writer(f)

            adultwriter.writerow(headers)
            adultwriter.writerows(matrix)

        return True

    def abort(self):
        self.want_abort = True

    def print_warning(self, var, row_num, row, headers, default_fill):
        warning_logger.warning('Adult :: Value at row {} col {} for variable {} should be blank, setting to default and continuing'.format(row_num + 2, headers.index(var), var))
        row[headers.index(var)] = str(default_fill.get(var))
        self.warnings = True

    # def convert_short_form_free_text_headers(self):

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
