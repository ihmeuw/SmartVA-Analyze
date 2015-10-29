from __future__ import print_function

import csv

from smartva.default_fill_data import (
    CHILD_DEFAULT_FILL as DEFAULT_FILL,
    CHILD_DEFAULT_FILL_SHORT as DEFAULT_FILL_SHORT
)
from smartva.answer_ranges import CHILD_RANGE_LIST as RANGE_LIST
from smartva.word_conversions import CHILD_WORDS_TO_VARS as WORDS_TO_VARS
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.utils.conversion_utils import additional_headers_and_values, check_skip_patterns
from smartva.utils import status_notifier
from smartva.neonate_pre_symptom_data import (
    DURATION_VARS,
    GENERATED_VARS_DATA,
    VAR_CONVERSION_MAP,
    RECODE_MAP,
    FREE_TEXT_VARS,
    SHORT_FORM_FREE_TEXT_CONVERSION,
    BINARY_CONVERSION_MAP,
    SKIP_PATTERN_DATA,
    DURATION_VARS_SPECIAL_CASE,
    DURATION_VARS_SHORT_FORM_DROP_LIST,
    WEIGHT_SD_DATA)

FILENAME_TEMPLATE = '{:s}-presymptom.csv'
DROP_PATTERN = '[a]([_\d]|dult)'


class NeonatePreSymptomPrep(PreSymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        PreSymptomPrep.__init__(self, input_file, output_dir, short_form)
        self.AGE_GROUP = 'neonate'

    def run(self):
        super(NeonatePreSymptomPrep, self).run()

        if self.short_form:
            default_fill = DEFAULT_FILL_SHORT
        else:
            default_fill = DEFAULT_FILL

        # Create a list of duration variables, dropping specified variables if using the short form.
        duration_vars = DURATION_VARS[:]
        if self.short_form:
            for var in DURATION_VARS_SHORT_FORM_DROP_LIST:
                duration_vars.remove(var)

        with open(self.input_file_path, 'rb') as fi:
            reader = csv.DictReader(fi)
            matrix = [row for row in reader]

        status_notifier.update({'sub_progress': (0, len(matrix))})

        headers = reader.fieldnames

        additional_data = {k: '' for k in duration_vars}
        additional_data.update(GENERATED_VARS_DATA)
        additional_headers, additional_values = additional_headers_and_values(headers, additional_data.items())

        headers.extend(additional_headers)
        self.rename_headers(headers, VAR_CONVERSION_MAP)

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
            self.rename_vars(row, VAR_CONVERSION_MAP)

            self.verify_answers_for_row(row, RANGE_LIST)

            self.convert_free_text_vars(row, FREE_TEXT_VARS, WORDS_TO_VARS)

            if self.short_form:
                word_list = [v for k, v in SHORT_FORM_FREE_TEXT_CONVERSION.items() if row[k] in [1, '1']]
                if word_list:
                    self.convert_free_text_words(row, word_list, WORDS_TO_VARS)

            self.recode_answers(row, RECODE_MAP)

            self.process_binary_vars(row, BINARY_CONVERSION_MAP.items())

            check_skip_patterns(row, SKIP_PATTERN_DATA, default_fill)
            # special case skip patterns

            self.calculate_duration_vars(row, duration_vars, DURATION_VARS_SPECIAL_CASE)

            self.validate_weight_vars(row)

            self.process_date_vars(row)

            self.process_weight_sd_vars(row, WEIGHT_SD_DATA)

            self.process_age_vars(row)

            self.fill_missing_data(row, default_fill)

        status_notifier.update({'sub_progress': None})

        self.write_output_file(headers, matrix)

        return True


"""
            # fix child agedays.  if it's blank give it a 0, if it's not, give it a 4
            if row[headers.index('c1_25b')] == '' or row[headers.index('c1_25b')] is None:
                row[headers.index('c1_25a')] = 0
            else:
                row[headers.index('c1_25a')] = 4

            if (row[headers.index('c1_25b')] != '' and int(row[headers.index('c1_25b')]) >= 1 and int(
                    row[headers.index('c1_25b')]) <= 28):
                row[headers.index('c1_26')] = 1
"""

"""
            index = headers.index('c4_33b')
            temp = row[headers.index('c4_33a')]
            if temp == '4':
                row[index] = row[headers_old.index('child_4_33a')]
"""
"""
            # added for shortform
            if self.shortform:
                index = headers.index('c1_22a')
                temp = row[headers_old.index('child_1_22')]
                if temp == '1':
                    row[index] = '1'
                if temp == '2':
                    row[index] = '2'
                if temp == '3':
                    row[index] = '4'
                if temp == '4':
                    row[index] = '5'
                if temp == '5':
                    row[index] = '6'
                if temp == '8':
                    row[index] = '8'
                if temp == '9':
                    row[index] = '9'
"""
"""
                index = headers.index('c4_08a')
                temp = row[headers_old.index('child_4_8')]
                if temp == '2':
                    row[index] = '1'
"""
