import abc
import csv
import os
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from stemming.porter2 import stem
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import value_or_default, additional_headers_and_values, check_skip_patterns

FILENAME_TEMPLATE = '{:s}-presymptom.csv'

DOB_VAR = 'g5_01'
SEX_VAR = 'g5_02'
AGE_VARS = ['g5_04']

TIME_FACTORS = {
    1: 365.0,
    2: 30.0,
    3: 7.0,
    4: 1.0,
    5: 1 / 24.0,
    6: 1 / 1440.0
}


def make_date(row, key):
    return date(int(row['{:s}y'.format(key)]),
                int(row['{:s}m'.format(key)]),
                int(row['{:s}d'.format(key)]))


def months_delta(date1, date2):
    delta = relativedelta(date1, date2)
    return abs(delta.years * 12 + delta.months)


class PreSymptomPrep(DataPrep):
    __metaclass__ = abc.ABCMeta

    def __init__(self, input_file, output_dir, short_form):
        super(PreSymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = None
        self.default_fill = None

    def _init_data_module(self):
        if self.short_form:
            self.default_fill = self.data_module.DEFAULT_FILL_SHORT
        else:
            self.default_fill = self.data_module.DEFAULT_FILL

    def run(self):
        super(PreSymptomPrep, self).run()

        status_logger.info('{} :: Processing pre-symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        # Create a list of duration variables, dropping specified variables if using the short form.
        duration_vars = self.data_module.DURATION_VARS[:]
        if self.short_form:
            for var in self.data_module.DURATION_VARS_SHORT_FORM_DROP_LIST:
                duration_vars.remove(var)

        with open(self.input_file_path, 'rb') as fi:
            reader = csv.DictReader(fi)
            matrix = [row for row in reader]

        status_notifier.update({'sub_progress': (0, len(matrix))})

        headers = reader.fieldnames

        additional_data = {k: '' for k in self.data_module.DURATION_VARS}
        additional_data.update({k: 0 for k in self.data_module.GENERATED_VARS_DATA})
        additional_headers, additional_values = additional_headers_and_values(headers, additional_data.items())

        headers.extend(additional_headers)
        self.rename_headers(headers, self.data_module.VAR_CONVERSION_MAP)

        # TODO - Review this and re-implement for DictWriter, if necessary.
        """
        drop_index_list = self.get_drop_index_list(headers, DROP_PATTERN)
        drop_index_list += self.get_drop_index_list(headers, 'child')
        drop_index_list += [headers.index('{}a'.format(header)) for header in DURATION_VARS]
        drop_index_list += [headers.index('{}b'.format(header)) for header in DURATION_VARS]
        """

        for index, row in enumerate(matrix):
            if self.want_abort:
                return False

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(zip(additional_headers, additional_values)))
            self.rename_vars(row, self.data_module.VAR_CONVERSION_MAP)

            self.verify_answers_for_row(row, self.data_module.RANGE_LIST)

            self.pre_processing_step(row)

            self.recode_answers(row, self.data_module.RECODE_MAP)

            self.process_binary_vars(row, self.data_module.BINARY_CONVERSION_MAP.items())

            check_skip_patterns(row, self.data_module.SKIP_PATTERN_DATA, self.default_fill)
            # special case skip patterns

            self.calculate_duration_vars(row, duration_vars, self.data_module.DURATION_VARS_SPECIAL_CASE)

            self.validate_weight_vars(row, self.data_module.WEIGHT_VARS)

            self.process_date_vars(row, self.data_module.DATE_VARS)

            self.process_age_vars(row)

            self.convert_free_text_vars(row, self.data_module.FREE_TEXT_VARS, self.data_module.WORDS_TO_VARS)

            if self.short_form:
                word_list = [v for k, v in self.data_module.SHORT_FORM_FREE_TEXT_CONVERSION.items()
                             if value_or_default(row[k]) == 1]
                if word_list:
                    self.convert_free_text_words(row, word_list, self.data_module.WORDS_TO_VARS)

            self.post_processing_step(row)

            self.fill_missing_data(row, self.default_fill)

        status_notifier.update({'sub_progress': None})

        self.write_output_file(headers, matrix)

        return True

    @abc.abstractmethod
    def pre_processing_step(self, row):
        pass

    @abc.abstractmethod
    def post_processing_step(self, row):
        self.process_weight_sd_vars(row, self.data_module.WEIGHT_SD_DATA)

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
                read_value: 'data_header' or value
            }

        :param row: Row of data.
        :param consolidation_map: Dictionary of read/write variables and their data counterparts.
        """
        for data_headers, data_map in consolidation_map.items():
            read_header, write_header = data_headers
            try:
                value = int(row[read_header])
            except ValueError:
                pass
            except KeyError:
                warning_logger.warning(
                    'SID: {} Variable \'{}\' does not exist.'.format(row['sid'], read_header))
            else:
                # Changed to allow arbitrary values to be used.
                # TODO - Maybe use '#' before var to indicate lookup.
                if value in data_map:
                    if isinstance(data_map[value], str):
                        row[write_header] = row[data_map[value]]
                    else:
                        row[write_header] = data_map[value]

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
            code_value = value_or_default(row[code_var])
            length_value = value_or_default(row[length_var])

            if var in special_case_vars and row[length_var] == '':
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
                # warning_logger.warning('Word {} map {}'.format(stem(word), word_map[stem(word)]))
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

    @staticmethod
    def process_age_vars(row):
        for age_var in AGE_VARS:
            years = value_or_default(row['{:s}a'.format(age_var)], float, [999, 9999])
            months = value_or_default(row['{:s}b'.format(age_var)], float, 99)
            days = value_or_default(row['{:s}c'.format(age_var)], float, 99)
            row['{:s}a'.format(age_var)] = years + (months / 12.0) + (days / 365.0)
            row['{:s}b'.format(age_var)] = (12.0 * years) + months + (days / 30.0)
            row['{:s}c'.format(age_var)] = (365.0 * years) + (30.0 * months) + days

    @staticmethod
    def validate_weight_vars(row, weight_vars):
        for var in weight_vars:
            row[var] = value_or_default(row[var], int, [0, 9999], '')

    @staticmethod
    def process_date_vars(row, date_vars):
        # Get an approximate date.
        # Add 'd' (day) 'm' (month) 'y' (years) to each var and process.
        date_invalid = {
            'd': (['', '99', 99], 1),
            'm': (['', '99', 99], 1),
            'y': (['', '999', 999, '9999', 9999], 0),
        }
        for var in date_vars:
            for val, val_data in date_invalid.items():
                var_name = var + val
                invalid_data, default = val_data
                if row[var_name] in invalid_data:
                    row[var_name] = default

    @staticmethod
    def process_weight_sd_vars(row, exam_date_vars, weight_sd_data):
        # Get most recent weight from medical records
        if int(row['{:s}y'.format(DOB_VAR)]):
            try:
                dob = make_date(row, DOB_VAR)
            except ValueError:
                pass
            else:

                exam_data = []
                for date_var, weight_var in exam_date_vars.items():
                    try:
                        exam_date = make_date(row, date_var)
                        exam_weight = float(row['{:s}b'.format(weight_var)])
                        exam_data.append((exam_date, exam_weight))
                    except ValueError:
                        # If the date is invalid or the weight isn't a number, skip this exam.
                        continue

                if exam_data:
                    latest_exam, latest_weight = sorted(exam_data, reverse=True)[0]

                    if latest_exam > dob:
                        age_at_exam_months = months_delta(latest_exam, dob)

                        if age_at_exam_months <= 60:
                            sex = int(row[SEX_VAR])
                            weight_kg = latest_weight / 1000

                            for sd_var, sd_data in weight_sd_data.items():
                                row[sd_var] = int(
                                    weight_kg < sd_data.get(sex, {}).get(age_at_exam_months, 0))

    def write_output_file(self, headers, matrix):
        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.DictWriter(fo, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matrix)
