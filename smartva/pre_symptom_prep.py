import abc
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from stemming.porter2 import stem

from smartva.data.answer_ranges import RANGE_LIST
from smartva.data_prep import DataPrep
from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import value_or_default, additional_headers_and_values, check_skip_patterns

INPUT_FILENAME_TEMPLATE = '{:s}-prepped.csv'
OUTPUT_FILENAME_TEMPLATE = '{:s}-presymptom.csv'

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
    """Prepare pre-symptom data for symptom processing.

    The main goal of this step is to verify and recode answers for further processing.
    Steps to accomplish this goal:
        Read intermediate data file
        Identify new headers and additional data to be added this step
        Verify answers
        Run pre-processing actions
        Process and recode answers
        Run post-processing actions
        Fill missing answers with default values
        Write new intermediate data file

    Subclasses must set the data_module property, which will get the class ready.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, working_dir_path, short_form):
        super(PreSymptomPrep, self).__init__(working_dir_path, short_form)

        self.INPUT_FILENAME_TEMPLATE = INPUT_FILENAME_TEMPLATE
        self.OUTPUT_FILENAME_TEMPLATE = OUTPUT_FILENAME_TEMPLATE

        self.input_dir_path = self.intermediate_dir
        self.output_dir_path = self.intermediate_dir

        self._data_module = None
        self.default_fill = None

    @property
    def data_module(self):
        return self._data_module

    @data_module.setter
    def data_module(self, value):
        assert self._data_module is None
        self._data_module = value

        self.AGE_GROUP = self.data_module.AGE_GROUP

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

        headers, matrix = DataPrep.read_input_file(self.input_file_path())

        status_notifier.update({'sub_progress': (0, len(matrix))})

        # Identify new headers and data to be included.
        additional_data = {k: '' for k in self.data_module.DURATION_VARS}
        additional_data.update({k: 0 for k in self.data_module.GENERATED_VARS_DATA})
        additional_headers, additional_values = additional_headers_and_values(headers, additional_data.items())

        headers.extend(additional_headers)
        self.rename_headers(headers, self.data_module.VAR_CONVERSION_MAP)

        # Make a list of headers to keep and to drop.
        keep_list = [header for header in headers if re.match(self.data_module.KEEP_PATTERN, header)]
        drop_list = (['{}a'.format(header) for header in duration_vars] +
                     ['{}b'.format(header) for header in duration_vars])

        # Prune headers and sort by 'sid', then anything that doesn't contain a digit at pos 1, then general vars.
        headers = sorted([header for header in headers if header in keep_list and header not in drop_list],
                         key=lambda t: (t != 'sid', t[1].isdigit(), not t.startswith('g'), t))

        for index, row in enumerate(matrix):
            self.check_abort()

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(zip(additional_headers, additional_values)))
            self.rename_vars(row, self.data_module.VAR_CONVERSION_MAP)

            self.verify_answers_for_row(row, RANGE_LIST)

            self.pre_processing_step(row)

            self.recode_answers(row, self.data_module.RECODE_MAP)

            self.process_binary_vars(row, self.data_module.BINARY_CONVERSION_MAP.items())

            check_skip_patterns(row, self.data_module.SKIP_PATTERN_DATA, self.default_fill)
            # special case skip patterns

            self.calculate_duration_vars(row, duration_vars, self.data_module.DURATION_VARS_SPECIAL_CASE)

            self.validate_weight_vars(row, self.data_module.WEIGHT_VARS)

            self.validate_date_vars(row, self.data_module.DATE_VARS)

            self.process_age_vars(row)

            self.convert_free_text_vars(row, self.data_module.FREE_TEXT_VARS, self.data_module.WORDS_TO_VARS)

            if self.short_form:
                word_list = [v for k, v in self.data_module.SHORT_FORM_FREE_TEXT_CONVERSION.items()
                             if value_or_default(row.get(k)) == 1]
                if word_list:
                    self.convert_free_text_words(row, word_list, self.data_module.WORDS_TO_VARS)

            self.post_processing_step(row)

            self.fill_missing_data(row, self.default_fill)

        status_notifier.update({'sub_progress': None})

        DataPrep.write_output_file(headers, matrix, self.output_file_path())

        return True

    def verify_answers_for_row(self, row, valid_range_data):
        """Verify answers in a row of data are valid. Log a warning when an invalid answer has been identified.

        Args:
            row (dict): Row of VA data.
            valid_range_data (dict): Map of answers and valid ranges.
        """
        for variable, range_list in valid_range_data.items():
            try:
                value = row[variable]
            except KeyError:
                pass  # Header not in data set.
            else:
                for answer in str(value).split():
                    try:
                        if int(answer) not in range_list:
                            warning_logger.warning(
                                'SID: {} variable \'{}\' has an illegal value {}. '
                                'Please see code book for legal values.'.format(row['sid'], variable, value))
                    except ValueError:
                        continue

    def recode_answers(self, row, consolidation_map):
        """Recode answers from data answers into new variables.

        Consolidation map dictionary format:
            (read_header, write_header): {
                read_value: 'data_header' or value
            }

        Args:
            row (dict): Row of VA data.
            consolidation_map (dict): Dictionary of read/write variables and their data counterparts.
        """
        for data_headers, data_map in consolidation_map.items():
            read_header, write_header = data_headers
            try:
                value = int(row[read_header])
            except ValueError:
                pass
            except KeyError:
                warning_logger.warning(
                    'SID: {} variable \'{}\' does not exist.'.format(row['sid'], read_header))
            else:
                # Changed to allow arbitrary values to be used.
                # TODO - Maybe use '#' before var to indicate lookup.
                if value in data_map:
                    if isinstance(data_map[value], str):
                        row[write_header] = row[data_map[value]]
                    else:
                        row[write_header] = data_map[value]

    def calculate_duration_vars(self, row, duration_vars, special_case_vars):
        """Calculate duration variables in days.

        Args:
            row (dict): Row of VA data.
            duration_vars (list): Answers which contain duration variables.
            special_case_vars (dict): Dictionary of special variables and their value if duration is blank.
        """
        for var in duration_vars:
            code_var, length_var = '{}a'.format(var), '{}b'.format(var)
            try:
                code_value = value_or_default(row[code_var])
                length_value = value_or_default(row[length_var])
            except KeyError as e:
                # Variable does not exist.
                warning_logger.debug('SID: {} variable \'{}\' does not exist. calculate_duration_vars'
                                     .format(row['sid'], e.message))
                continue

            if var in special_case_vars and row[length_var] == '':
                row[var] = special_case_vars[var]
            else:
                row[var] = TIME_FACTORS.get(code_value, 0) * length_value

    def convert_free_text_words(self, row, input_word_list, word_map):
        """Process free text word lists into binary variables.

        Args:
            row (dict): Row of VA data.
            input_word_list (list): List of free text words to process.
            word_map (dict): Dictionary of words and variables.
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

    def convert_free_text_vars(self, row, data_headers, word_map):
        """Process all free text data from a list of data headers into binary variables.

        Args:
            row (dict): Row of VA data.
            data_headers (list): Answers which contain free text data.
            word_map (dict): Dictionary of words and variables.
        """
        for data_header in data_headers:
            if row[data_header]:
                word_list = row[data_header].split(' ')
                self.convert_free_text_words(row, word_list, word_map)

    def fill_missing_data(self, row, default_fill):
        """Fill missing data with default fill values.

        Args:
            row (dict): Row of VA data.
            default_fill (dict): Dictionary of headers and default values.
        """
        for variable, value in default_fill.items():
            try:
                if row[variable] == '':
                    row[variable] = value
            except KeyError as e:
                # Variable does not exist.
                warning_logger.debug('SID: {} variable \'{}\' does not exist. fill_missing_data'
                                     .format(row['sid'], e.message))
                continue

    def process_age_vars(self, row):
        """Calculate and store age in years, months, and days.

        Args:
            row (dict): Row of VA data.
        """
        for age_var in AGE_VARS:
            years = value_or_default(row['{:s}a'.format(age_var)], float, [999, 9999])
            months = value_or_default(row['{:s}b'.format(age_var)], float, 99)
            days = value_or_default(row['{:s}c'.format(age_var)], float, 99)
            row['{:s}a'.format(age_var)] = years + (months / 12.0) + (days / 365.0)
            row['{:s}b'.format(age_var)] = (12.0 * years) + months + (days / 30.0)
            row['{:s}c'.format(age_var)] = (365.0 * years) + (30.0 * months) + days

    def validate_weight_vars(self, row, weight_vars):
        """Replace invalid weight data with a default value.

        Args:
            row (dict): Row of VA data.
            weight_vars (list): Answers which contain weight data.
        """
        for var in weight_vars:
            row[var] = value_or_default(row[var], int, [0, 9999], '')

    def validate_date_vars(self, row, date_vars):
        """Try to get an approximate date by replacing invalid values with defaults.

        Args:
            row (dict): Row of VA data.
            date_vars (dict): Answers which contain date data.
        """
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

    def process_weight_sd_vars(self, row, exam_date_vars, weight_sd_data):
        # Get most recent weight from medical records
        """Calculate and store SD value for weight at most recent exam.

        Weight SD data Format:
            'var' (str): {
                SEX (int): SEX_SD_DATA (dict)
            }

        Args:
            row (dict): Row of VA data.
            exam_date_vars (dict): Answers which contain exam dates.
            weight_sd_data (dict): Map of variable to store and applicable SD data.
        """
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

    def fix_rash_length(self, row):
        """Only consider values in days for child rash data.

        Args:
            row: Row of VA data.
        """
        if int(row['c4_33a']) != 4:
            row['c4_33b'] = 0
