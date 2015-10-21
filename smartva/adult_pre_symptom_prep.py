import csv
import os

from smartva.default_fill_data import ADULT_DEFAULT_FILL, ADULT_DEFAULT_FILL_SHORT
from smartva.answer_ranges import ADULT_RANGE_LIST
from smartva.pre_symptom_prep import PreSymptomPrep
from smartva.word_conversions import ADULT_WORDS_TO_VARS
from smartva.loggers import status_logger
from smartva.utils import status_notifier, get_item_count
from smartva.adult_pre_symptom_data import (
    GENERATED_HEADERS_DATA,
    HEADER_CONVERSION_MAP,
    RECODE_MAP,
    BINARY_CONVERSION_MAP,
    SHORT_FORM_FREE_TEXT_CONVERSION,
    FREE_TEXT_HEADERS,
    SKIP_PATTERN_DATA,
    DURATION_VARS,
    DURATION_VARS_SHORT_FORM_DROP_LIST,
    DURATION_VARS_SPECIAL_CASE
)
from smartva.utils.conversion_utils import (
    additional_headers_and_values,
    check_skip_patterns
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

        duration_vars = DURATION_VARS[:]

        if self.short_form:
            for var in DURATION_VARS_SHORT_FORM_DROP_LIST:
                duration_vars.remove(var)

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.writer(fo)

            with open(self.input_file_path, 'rb') as fi:
                reader = csv.reader(fi)
                records = get_item_count(reader, fi) - 1
                status_notifier.update({'sub_progress': (0, records)})

                headers = next(reader)

                additional_headers_data = GENERATED_HEADERS_DATA + [(k, '') for k in DURATION_VARS]
                additional_headers, additional_values = additional_headers_and_values(headers, additional_headers_data)

                headers.extend(additional_headers)

                self.rename_headers(headers, HEADER_CONVERSION_MAP)

                drop_index_list = self.get_drop_index_list(headers, DROP_PATTERN)
                drop_index_list += self.get_drop_index_list(headers, 'adult')
                drop_index_list += [headers.index('{}a'.format(header)) for header in DURATION_VARS]
                drop_index_list += [headers.index('{}b'.format(header)) for header in DURATION_VARS]
                drop_index_list += [headers.index('a4_02')]

                writer.writerow(self.drop_from_list(headers, drop_index_list))

                for index, row in enumerate(reader):
                    if self.want_abort:
                        return False

                    status_notifier.update({'sub_progress': (index,)})

                    new_row = row + additional_values
                    
                    self.verify_answers_for_row(headers, new_row, ADULT_RANGE_LIST)

                    self.convert_free_text_headers(headers, new_row, FREE_TEXT_HEADERS, ADULT_WORDS_TO_VARS)

                    if self.short_form:
                        word_list = [v for k, v in SHORT_FORM_FREE_TEXT_CONVERSION.items() if
                                     new_row[headers.index(k)] in [1, '1']]
                        if word_list:
                            self.convert_free_text_words(headers, new_row, word_list, ADULT_WORDS_TO_VARS)

                    self.recode_answers(headers, new_row, RECODE_MAP)

                    self.convert_binary_variables(headers, new_row, BINARY_CONVERSION_MAP.items())
                
                    check_skip_patterns(headers, new_row, SKIP_PATTERN_DATA)

                    self.fill_missing_data(headers, new_row, default_fill)

                    self.calculate_duration_variables(headers, new_row, duration_vars, DURATION_VARS_SPECIAL_CASE)

                    writer.writerow(self.drop_from_list(new_row, drop_index_list))

        status_notifier.update({'sub_progress': None})

        return True
