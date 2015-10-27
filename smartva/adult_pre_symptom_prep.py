import csv
import os

from smartva.default_fill_data import ADULT_DEFAULT_FILL, ADULT_DEFAULT_FILL_SHORT
from smartva.answer_ranges import ADULT_RANGE_LIST
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.word_conversions import ADULT_WORDS_TO_VARS
from smartva.loggers import status_logger
from smartva.utils import status_notifier
from smartva.adult_pre_symptom_data import (
    GENERATED_VARS_DATA,
    VAR_CONVERSION_MAP,
    RECODE_MAP,
    BINARY_CONVERSION_MAP,
    SHORT_FORM_FREE_TEXT_CONVERSION,
    FREE_TEXT_VARS,
    SKIP_PATTERN_DATA,
    DURATION_VARS,
    DURATION_VARS_SHORT_FORM_DROP_LIST,
    DURATION_VARS_SPECIAL_CASE
)
from smartva.utils.conversion_utils import (
    additional_headers_and_values,
    check_skip_patterns,
)

FILENAME_TEMPLATE = '{:s}-presymptom.csv'
DROP_PATTERN = '[cpn]([_\d]|hild|omplications|rovider|eonate)'


class AdultPreSymptomPrep(PreSymptomPrep):
    def __init__(self, input_file, output_dir, short_form):
        PreSymptomPrep.__init__(self, input_file, output_dir, short_form)
        self.AGE_GROUP = 'adult'

    def run(self):
        status_logger.info('{} :: Processing pre-symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        if self.short_form:
            default_fill = ADULT_DEFAULT_FILL_SHORT
        else:
            default_fill = ADULT_DEFAULT_FILL

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
        drop_index_list += self.get_drop_index_list(headers, 'adult')
        drop_index_list += [headers.index('{}a'.format(header)) for header in DURATION_VARS]
        drop_index_list += [headers.index('{}b'.format(header)) for header in DURATION_VARS]
        drop_index_list += [headers.index('a4_02')]
        """

        for index, row in enumerate(matrix):
            if self.want_abort:
                return False

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(zip(additional_headers, additional_values)))
            self.rename_vars(row, VAR_CONVERSION_MAP)

            self.verify_answers_for_row(row, ADULT_RANGE_LIST)

            self.convert_free_text_vars(row, FREE_TEXT_VARS, ADULT_WORDS_TO_VARS)

            if self.short_form:
                word_list = [v for k, v in SHORT_FORM_FREE_TEXT_CONVERSION.items() if row[k] in [1, '1']]
                if word_list:
                    self.convert_free_text_words(row, word_list, ADULT_WORDS_TO_VARS)

            self.recode_answers(row, RECODE_MAP)

            self.process_binary_vars(row, BINARY_CONVERSION_MAP.items())

            check_skip_patterns(row, SKIP_PATTERN_DATA)

            self.fill_missing_data(row, default_fill)

            self.calculate_duration_vars(row, duration_vars, DURATION_VARS_SPECIAL_CASE)

        status_notifier.update({'sub_progress': None})

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.DictWriter(fo, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matrix)

        return True
