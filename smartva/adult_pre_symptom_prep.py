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
    BINARY_CONVERSION_MAP
)
from smartva.conversion_utils import ConversionError, convert_binary_variable

FILENAME_TEMPLATE = '{:s}-presymptom.csv'


class AdultPreSymptomPrep(object):
    AGE_GROUP = 'adult'

    def __init__(self, input_file, output_dir, short_form):
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.short_form = short_form

        self.want_abort = False
        self.warnings = False

    @staticmethod
    def additional_headers_and_values(headers, additional_headers_data):
        """
        Calculate necessary additional headers and values based on comparing existing headers to additional header data.

        :param headers:
        :return:
        """
        additional_headers = []
        additional_values = []
        for k, v in additional_headers_data:
            if k not in headers:
                additional_headers.append(k)
                additional_values.append(v)

        return additional_headers, additional_values

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

            additional_headers, additional_values = self.additional_headers_and_values(headers, GENERATED_HEADERS_DATA)
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

        # make a copy of the new list
        headers_old = copy.deepcopy(headers)

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
                        row[headers.index(write_header)] = row[headers_old.index(data_map[value])]

            # Convert binary variables
            for data_header, data_map in BINARY_CONVERSION_MAP.items():
                try:
                    convert_binary_variable(headers, row, data_header, data_map)
                except ConversionError as e:
                    warning_logger.debug(e.message)

        # check skip patterns
        for i, row in enumerate(matrix):
            # i starts at 0, header row is 1 in excel, so do i+2 for the actual data row
            a2_02 = row[headers.index('a2_02')]
            if a2_02 != '1':
                a2_03a = row[headers.index('a2_03a')]
                if not (a2_03a is None or a2_03a == ''):
                    self.print_warning('a2_03a', i, row, headers, default_fill)
                a2_03b = row[headers.index('a2_03b')]
                if not (a2_03b is None or a2_03b == ''):
                    self.print_warning('a2_03b', i, row, headers, default_fill)
                a2_04 = row[headers.index('a2_04')]
                if not (a2_04 is None or a2_04 == ''):
                    self.print_warning('a2_04', i, row, headers, default_fill)
                a2_05 = row[headers.index('a2_04')]
                if not (a2_05 is None or a2_05 == ''):
                    self.print_warning('a2_05', i, row, headers, default_fill)
                a2_06 = row[headers.index('a2_04')]
                if not (a2_06 is None or a2_06 == ''):
                    self.print_warning('a2_06', i, row, headers, default_fill)
            a2_07 = row[headers.index('a2_07')]
            if a2_07 != '1':
                a2_08a = row[headers.index('a2_08a')]
                if not (a2_08a is None or a2_08a == ''):
                    self.print_warning('a2_08a', i, row, headers, default_fill)
                a2_08b = row[headers.index('a2_08b')]
                if not (a2_08b is None or a2_08b == ''):
                    self.print_warning('a2_08b', i, row, headers, default_fill)
                a2_09_1a = row[headers.index('a2_09_1a')]
                if not (a2_09_1a is None or a2_09_1a == ''):
                    self.print_warning('a2_09_1a', i, row, headers, default_fill)
                a2_09_1b = row[headers.index('a2_09_1b')]
                if not (a2_09_1b is None or a2_09_1b == ''):
                    self.print_warning('a2_09_1b', i, row, headers, default_fill)
                a2_09_2a = row[headers.index('a2_09_2a')]
                if not (a2_09_2a is None or a2_09_2a == '' or a2_09_2a == '0'):
                    self.print_warning('a2_09_2a', i, row, headers, default_fill)

            a2_10 = row[headers.index('a2_10')]
            if a2_10 != '1':
                a2_11 = row[headers.index('a2_11')]
                if not (a2_11 is None or a2_11 == ''):
                    self.print_warning('a2_11', i, row, headers, default_fill)
            a2_13 = row[headers.index('a2_13')]
            if a2_13 != '1':
                a2_14 = row[headers.index('a2_14')]
                if not (a2_14 is None or a2_14 == ''):
                    self.print_warning('a2_14', i, row, headers, default_fill)
            a2_14 = row[headers.index('a2_14')]
            if a2_13 != '1' or a2_14 != '1':
                a2_15a = row[headers.index('a2_15a')]
                if not (a2_15a is None or a2_15a == ''):
                    self.print_warning('a2_15a', i, row, headers, default_fill)
                a2_15b = row[headers.index('a2_15b')]
                if not (a2_15b is None or a2_15b == ''):
                    self.print_warning('a2_15b', i, row, headers, default_fill)
            a2_18 = row[headers.index('a2_18')]
            if a2_18 != '1':
                a2_19 = row[headers.index('a2_19')]
                if not (a2_19 is None or a2_19 == ''):
                    self.print_warning('a2_19', i, row, headers, default_fill)
            a2_21 = row[headers.index('a2_21')]
            if a2_21 != '1':
                a2_22a = row[headers.index('a2_22a')]
                if not (a2_22a is None or a2_22a == ''):
                    self.print_warning('a2_22a', i, row, headers, default_fill)
                a2_22b = row[headers.index('a2_22b')]
                if not (a2_22b is None or a2_22b == '' or a2_22b == '0'):
                    self.print_warning('a2_22b', i, row, headers, default_fill)
            a2_23 = row[headers.index('a2_23')]
            if a2_23 != '1':
                a2_24a = row[headers.index('a2_24a')]
                if not (a2_24a is None or a2_24a == ''):
                    self.print_warning('a2_24a', i, row, headers, default_fill)
                a2_24b = row[headers.index('a2_24b')]
                if not (a2_24b is None or a2_24b == '' or a2_24b == '0'):
                    self.print_warning('a2_24b', i, row, headers, default_fill)
            a2_25 = row[headers.index('a2_25')]
            if a2_25 != '1':
                a2_26a = row[headers.index('a2_26a')]
                if not (a2_26a is None or a2_26a == ''):
                    self.print_warning('a2_26a', i, row, headers, default_fill)
                a2_26b = row[headers.index('a2_26b')]
                if not (a2_26b is None or a2_26b == '' or a2_26b == '0'):
                    self.print_warning('a2_26b', i, row, headers, default_fill)
            a2_27 = row[headers.index('a2_27')]
            if a2_27 != '1':
                a2_28a = row[headers.index('a2_28a')]
                if not (a2_28a is None or a2_28a == ''):
                    self.print_warning('a2_28a', i, row, headers, default_fill)
                a2_28b = row[headers.index('a2_28b')]
                if not (a2_28b is None or a2_28b == '' or a2_28b == '0'):
                    self.print_warning('a2_28b', i, row, headers, default_fill)
            a2_32 = row[headers.index('a2_32')]
            if a2_32 != '1':
                a2_33a = row[headers.index('a2_33a')]
                if not (a2_33a is None or a2_33a == ''):
                    self.print_warning('a2_33a', i, row, headers, default_fill)
                a2_33b = row[headers.index('a2_33b')]
                if not (a2_33b is None or a2_33b == '' or a2_33b == '0'):
                    self.print_warning('a2_33b', i, row, headers, default_fill)
                a2_34 = row[headers.index('a2_34')]
                if not (a2_34 is None or a2_34 == ''):
                    self.print_warning('a2_34', i, row, headers, default_fill)
                a2_35 = row[headers.index('a2_35')]
                if not (a2_35 is None or a2_35 == ''):
                    self.print_warning('a2_35', i, row, headers, default_fill)
            a2_36 = row[headers.index('a2_36')]
            if a2_36 != '1':
                a2_37a = row[headers.index('a2_37a')]
                if not (a2_37a is None or a2_37a == ''):
                    self.print_warning('a2_37a', i, row, headers, default_fill)
                a2_37b = row[headers.index('a2_37b')]
                if not (a2_37b is None or a2_37b == '' or a2_37b == '0'):
                    self.print_warning('a2_37b', i, row, headers, default_fill)
                a2_38 = row[headers.index('a2_38')]
                if not (a2_38 is None or a2_38 == ''):
                    self.print_warning('a2_38', i, row, headers, default_fill)
                a2_39_1 = row[headers.index('a2_39_1')]
                if not (a2_39_1 is None or a2_39_1 == ''):
                    self.print_warning('a2_39_1', i, row, headers, default_fill)

            a2_40 = row[headers.index('a2_40')]
            if a2_40 != '1':
                a2_41a = row[headers.index('a2_41a')]
                if not (a2_41a is None or a2_41a == ''):
                    self.print_warning('a2_41a', i, row, headers, default_fill)
                a2_41b = row[headers.index('a2_41b')]
                if not (a2_41b is None or a2_41b == '' or a2_41b == '0'):
                    self.print_warning('a2_41b', i, row, headers, default_fill)
            a2_43 = row[headers.index('a2_43')]
            if a2_43 != '1':
                a2_44 = row[headers.index('a2_44')]
                if not (a2_44 is None or a2_44 == ''):
                    self.print_warning('a2_44', i, row, headers, default_fill)
                a2_45 = row[headers.index('a2_45')]
                if not (a2_45 is None or a2_45 == ''):
                    self.print_warning('a2_45', i, row, headers, default_fill)
                a2_46a = row[headers.index('a2_46a')]
                if not (a2_46a is None or a2_46a == ''):
                    self.print_warning('a2_46a', i, row, headers, default_fill)
                a2_46b = row[headers.index('a2_46b')]
                if not (a2_46b is None or a2_46b == ''):
                    self.print_warning('a2_46b', i, row, headers, default_fill)
            a2_47 = row[headers.index('a2_47')]
            if a2_47 != '1':
                a2_48a = row[headers.index('a2_48a')]
                if not (a2_48a is None or a2_48a == ''):
                    self.print_warning('a2_48a', i, row, headers, default_fill)
                a2_48b = row[headers.index('a2_48b')]
                if not (a2_48b is None or a2_48b == ''):
                    self.print_warning('a2_48b', i, row, headers, default_fill)
            a2_50 = row[headers.index('a2_50')]
            if a2_50 != '1':
                a2_51 = row[headers.index('a2_51')]
                if not (a2_51 is None or a2_51 == ''):
                    self.print_warning('a2_51', i, row, headers, default_fill)
            a2_53 = row[headers.index('a2_53')]
            if a2_53 != '1':
                a2_54a = row[headers.index('a2_54a')]
                if not (a2_54a is None or a2_54a == ''):
                    self.print_warning('a2_54a', i, row, headers, default_fill)
                a2_54b = row[headers.index('a2_54b')]
                if not (a2_54b is None or a2_54b == '' or a2_54b == '0'):
                    self.print_warning('a2_54b', i, row, headers, default_fill)
                a2_55 = row[headers.index('a2_55')]
                if not (a2_55 is None or a2_55 == ''):
                    self.print_warning('a2_55', i, row, headers, default_fill)
                a2_56 = row[headers.index('a2_56')]
                if not (a2_56 is None or a2_56 == ''):
                    self.print_warning('a2_56', i, row, headers, default_fill)
            a2_57 = row[headers.index('a2_57')]
            if a2_57 != '1':
                a2_58a = row[headers.index('a2_58a')]
                if not (a2_58a is None or a2_58a == ''):
                    self.print_warning('a2_58a', i, row, headers, default_fill)
                a2_58b = row[headers.index('a2_58b')]
                if not (a2_58b is None or a2_58b == '' or a2_58b == '0'):
                    self.print_warning('a2_58b', i, row, headers, default_fill)
                a2_59 = row[headers.index('a2_59')]
                if not (a2_59 is None or a2_59 == ''):
                    self.print_warning('a2_59', i, row, headers, default_fill)
            a2_61 = row[headers.index('a2_61')]
            if a2_61 != '1':
                a2_62a = row[headers.index('a2_62a')]
                if not (a2_62a is None or a2_62a == ''):
                    self.print_warning('a2_62a', i, row, headers, default_fill)
                a2_62b = row[headers.index('a2_62b')]
                if not (a2_62b is None or a2_62b == '' or a2_62b == '0'):
                    self.print_warning('a2_62b', i, row, headers, default_fill)
                a2_63_1 = row[headers.index('a2_63_1')]
                if not (a2_63_1 is None or a2_63_1 == ''):
                    self.print_warning('a2_63_1', i, row, headers, default_fill)

            a2_64 = row[headers.index('a2_64')]
            if a2_64 != '1':
                a2_65a = row[headers.index('a2_65a')]
                if not (a2_65a is None or a2_65a == ''):
                    self.print_warning('a2_65a', i, row, headers, default_fill)
                a2_65b = row[headers.index('a2_65b')]
                if not (a2_65b is None or a2_65b == '' or a2_65b == '0'):
                    self.print_warning('a2_65b', i, row, headers, default_fill)
                a2_66 = row[headers.index('a2_66')]
                if not (a2_66 is None or a2_66 == ''):
                    self.print_warning('a2_66', i, row, headers, default_fill)
            a2_67 = row[headers.index('a2_67')]
            if a2_67 != '1':
                a2_68a = row[headers.index('a2_68a')]
                if not (a2_68a is None or a2_68a == ''):
                    self.print_warning('a2_68a', i, row, headers, default_fill)
                a2_68b = row[headers.index('a2_68b')]
                if not (a2_68b is None or a2_68b == '' or a2_68b == '0'):
                    self.print_warning('a2_68b', i, row, headers, default_fill)
            a2_69 = row[headers.index('a2_69')]
            if a2_69 != '1':
                a2_70a = row[headers.index('a2_70a')]
                if not (a2_70a is None or a2_70a == ''):
                    self.print_warning('a2_70a', i, row, headers, default_fill)
                a2_70b = row[headers.index('a2_70b')]
                if not (a2_70b is None or a2_70b == '' or a2_70b == '0'):
                    self.print_warning('a2_70b', i, row, headers, default_fill)
                a2_71 = row[headers.index('a2_71')]
                if not (a2_71 is None or a2_71 == ''):
                    self.print_warning('a2_71', i, row, headers, default_fill)
            a2_72 = row[headers.index('a2_72')]
            if a2_72 != '1':
                a2_73a = row[headers.index('a2_73a')]
                if not (a2_73a is None or a2_73a == ''):
                    self.print_warning('a2_73a', i, row, headers, default_fill)
                a2_73b = row[headers.index('a2_73b')]
                if not (a2_73b is None or a2_73b == '' or a2_73b == '0'):
                    self.print_warning('a2_73b', i, row, headers, default_fill)
            a2_74 = row[headers.index('a2_74')]
            if a2_74 != '1':
                a2_76a = row[headers.index('a2_76a')]
                if not (a2_76a is None or a2_76a == ''):
                    self.print_warning('a2_76a', i, row, headers, default_fill)
                a2_76b = row[headers.index('a2_76b')]
                if not (a2_76b is None or a2_76b == '' or a2_76b == '0'):
                    self.print_warning('a2_76b', i, row, headers, default_fill)
                a2_75 = row[headers.index('a2_75')]
                if not (a2_75 is None or a2_75 == ''):
                    self.print_warning('a2_75', i, row, headers, default_fill)
                a2_77 = row[headers.index('a2_77')]
                if not (a2_77 is None or a2_77 == ''):
                    self.print_warning('a2_77', i, row, headers, default_fill)
            a2_78 = row[headers.index('a2_78')]
            if a2_78 != '1':
                a2_79a = row[headers.index('a2_79a')]
                if not (a2_79a is None or a2_79a == ''):
                    self.print_warning('a2_79a', i, row, headers, default_fill)
                a2_79b = row[headers.index('a2_79b')]
                if not (a2_79b is None or a2_79b == '' or a2_79b == '0'):
                    self.print_warning('a2_79b', i, row, headers, default_fill)
                a2_80 = row[headers.index('a2_80')]
                if not (a2_80 is None or a2_80 == ''):
                    self.print_warning('a2_80', i, row, headers, default_fill)
            a2_82 = row[headers.index('a2_82')]
            if a2_82 != '1':
                a2_83a = row[headers.index('a2_83a')]
                if not (a2_83a is None or a2_83a == ''):
                    self.print_warning('a2_83a', i, row, headers, default_fill)
                a2_83b = row[headers.index('a2_83b')]
                if not (a2_83b is None or a2_83b == '' or a2_83b == '0'):
                    self.print_warning('a2_83b', i, row, headers, default_fill)
                a2_84 = row[headers.index('a2_84')]
                if not (a2_84 is None or a2_84 == ''):
                    self.print_warning('a2_84', i, row, headers, default_fill)
            a2_85 = row[headers.index('a2_85')]
            if a2_85 != '1':
                a2_86a = row[headers.index('a2_86a')]
                if not (a2_86a is None or a2_86a == ''):
                    self.print_warning('a2_86a', i, row, headers, default_fill)
                a2_86b = row[headers.index('a2_86b')]
                if not (a2_86b is None or a2_86b == '' or a2_86b == '0'):
                    self.print_warning('a2_86b', i, row, headers, default_fill)
                a2_87_1 = row[headers.index('a2_87_1')]
                if not (a2_87_1 is None or a2_87_1 == '' or a2_87_1 == '0'):
                    self.print_warning('a2_87_1', i, row, headers, default_fill)
                a2_87_10a = row[headers.index('a2_87_10a')]
                if not (a2_87_10a is None or a2_87_10a == '' or a2_87_10a == '0'):
                    self.print_warning('a2_87_10a', i, row, headers, default_fill)
                a2_87_10b = row[headers.index('a2_87_10b')]
                a2_87_10b_split = a2_87_10b.split(' ')
                if not (a2_87_10b is None or a2_87_10b == '' or '0' in a2_87_10b_split):
                    self.print_warning('a2_87_10b', i, row, headers, default_fill)
                a2_87_2 = row[headers.index('a2_87_2')]
                if not (a2_87_2 is None or a2_87_2 == '' or a2_87_2 == '0'):
                    self.print_warning('a2_87_2', i, row, headers, default_fill)
                a2_87_3 = row[headers.index('a2_87_3')]
                if not (a2_87_3 is None or a2_87_3 == '' or a2_87_3 == '0'):
                    self.print_warning('a2_87_3', i, row, headers, default_fill)
                a2_87_4 = row[headers.index('a2_87_4')]
                if not (a2_87_4 is None or a2_87_4 == '' or a2_87_4 == '0'):
                    self.print_warning('a2_87_4', i, row, headers, default_fill)
                a2_87_5 = row[headers.index('a2_87_5')]
                if not (a2_87_5 is None or a2_87_5 == '' or a2_87_5 == '0'):
                    self.print_warning('a2_87_5', i, row, headers, default_fill)
                a2_87_6 = row[headers.index('a2_87_6')]
                if not (a2_87_6 is None or a2_87_6 == '' or a2_87_6 == '0'):
                    self.print_warning('a2_87_6', i, row, headers, default_fill)
                a2_87_7 = row[headers.index('a2_87_7')]
                if not (a2_87_7 is None or a2_87_7 == '' or a2_87_7 == '0'):
                    self.print_warning('a2_87_7', i, row, headers, default_fill)
                a2_87_8 = row[headers.index('a2_87_8')]
                if not (a2_87_8 is None or a2_87_8 == '' or a2_87_8 == '0'):
                    self.print_warning('a2_87_8', i, row, headers, default_fill)
                a2_87_9 = row[headers.index('a2_87_9')]
                if not (a2_87_9 is None or a2_87_9 == '' or a2_87_9 == '0'):
                    self.print_warning('a2_87_9', i, row, headers, default_fill)
            a4_01 = row[headers.index('a4_01')]
            if a4_01 != '1':
                a4_02_1 = row[headers.index('a4_02_1')]
                if not (a4_02_1 is None or a4_02_1 == '' or a4_02_1 == '0'):
                    self.print_warning('a4_02_1', i, row, headers, default_fill)
                a4_02_2 = row[headers.index('a4_02_2')]
                if not (a4_02_2 is None or a4_02_2 == '' or a4_02_2 == '0'):
                    self.print_warning('a4_02_2', i, row, headers, default_fill)
                a4_02_3 = row[headers.index('a4_02_3')]
                if not (a4_02_3 is None or a4_02_3 == '' or a4_02_3 == '0'):
                    self.print_warning('a4_02_3', i, row, headers, default_fill)
                a4_02_4 = row[headers.index('a4_02_4')]
                if not (a4_02_4 is None or a4_02_4 == '' or a4_02_4 == '0'):
                    self.print_warning('a4_02_3', i, row, headers, default_fill)
                a4_02_5a = row[headers.index('a4_02_5a')]
                if not (a4_02_5a is None or a4_02_5a == '' or a4_02_5a == '0'):
                    self.print_warning('a4_02_5a', i, row, headers, default_fill)
                a4_02_5b = row[headers.index('a4_02_5b')]
                if not (a4_02_5b is None or a4_02_5b == ''):
                    self.print_warning('a4_02_5b', i, row, headers, default_fill)
                a4_02_6 = row[headers.index('a4_02_6')]
                if not (a4_02_6 is None or a4_02_6 == '' or a4_02_6 == '0'):
                    self.print_warning('a4_02_6', i, row, headers, default_fill)
                a4_02_7 = row[headers.index('a4_02_7')]
                if not (a4_02_7 is None or a4_02_7 == '' or a4_02_7 == '0'):
                    self.print_warning('a4_02_7', i, row, headers, default_fill)
            a4_02_1 = row[headers.index('a4_02_1')]
            if a4_02_1 != '1' or a4_01 != '1':
                a4_04 = row[headers.index('a4_04')]
                if not (a4_04 is None or a4_04 == ''):
                    self.print_warning('a4_04', i, row, headers, default_fill)
            a4_05 = row[headers.index('a4_05')]
            if a4_05 != '1':
                a4_06 = row[headers.index('a4_06')]
                if not (a4_06 is None or a4_06 == ''):
                    self.print_warning('a4_06', i, row, headers, default_fill)
            a5_01_8 = row[headers.index('a5_01_8')]
            if a5_01_8 == '1':
                a5_04a = row[headers.index('a5_04a')]
                if not (a5_04a is None or a5_04a == ''):
                    self.print_warning('a5_04a', i, row, headers, default_fill)
                a5_04b = row[headers.index('a5_04b')]
                if not (a5_04b is None or a5_04b == '' or a5_04b == '0'):
                    self.print_warning('a5_04b', i, row, headers, default_fill)
                a5_02 = row[headers.index('a5_02')]
                if not (a5_02 is None or a5_02 == ''):
                    self.print_warning('a5_02', i, row, headers, default_fill)
            a5_02 = row[headers.index('a5_02')]
            if a5_02 == '1' or a5_01_8 == '1':
                a5_03 = row[headers.index('a5_03')]
                if not (a5_03 is None or a5_03 == ''):
                    self.print_warning('a5_03', i, row, headers, default_fill)
            a6_01 = row[headers.index('a6_01')]
            if a6_01 != '1':
                a6_02_1 = row[headers.index('a6_02_1')]
                if not (a6_02_1 is None or a6_02_1 == '' or a6_02_1 == '0'):
                    self.print_warning('a6_02_1', i, row, headers, default_fill)
                a6_02_2 = row[headers.index('a6_02_2')]
                if not (a6_02_2 is None or a6_02_2 == '' or a6_02_2 == '0'):
                    self.print_warning('a6_02_2', i, row, headers, default_fill)
                a6_02_3 = row[headers.index('a6_02_3')]
                if not (a6_02_3 is None or a6_02_3 == '' or a6_02_3 == '0'):
                    self.print_warning('a6_02_3', i, row, headers, default_fill)
                a6_02_4 = row[headers.index('a6_02_4')]
                if not (a6_02_4 is None or a6_02_4 == '' or a6_02_4 == '0'):
                    self.print_warning('a6_02_4', i, row, headers, default_fill)
                a6_02_5 = row[headers.index('a6_02_5')]
                if not (a6_02_5 is None or a6_02_5 == '' or a6_02_5 == '0'):
                    self.print_warning('a6_02_5', i, row, headers, default_fill)
                a6_02_6 = row[headers.index('a6_02_6')]
                if not (a6_02_6 is None or a6_02_6 == '' or a6_02_6 == '0'):
                    self.print_warning('a6_02_6', i, row, headers, default_fill)

                a6_02_8 = row[headers.index('a6_02_8')]
                if not (a6_02_8 is None or a6_02_8 == '' or a6_02_8 == '0'):
                    self.print_warning('a6_02_8', i, row, headers, default_fill)
                a6_02_9 = row[headers.index('a6_02_9')]
                if not (a6_02_9 is None or a6_02_9 == '' or a6_02_9 == '0'):
                    self.print_warning('a6_02_9', i, row, headers, default_fill)
                a6_02_10 = row[headers.index('a6_02_10')]
                if not (a6_02_10 is None or a6_02_10 == '' or a6_02_10 == '0'):
                    self.print_warning('a6_02_10', i, row, headers, default_fill)
                a6_02_11 = row[headers.index('a6_02_11')]
                if not (a6_02_11 is None or a6_02_11 == '' or a6_02_11 == '0'):
                    self.print_warning('a6_02_11', i, row, headers, default_fill)
                a6_02_12a = row[headers.index('a6_02_12a')]
                if not (a6_02_12a is None or a6_02_12a == '' or a6_02_12a == '0'):
                    self.print_warning('a6_02_12a', i, row, headers, default_fill)

                a6_02_13 = row[headers.index('a6_02_13')]
                if not (a6_02_13 is None or a6_02_13 == '' or a6_02_13 == '0'):
                    self.print_warning('a6_02_13', i, row, headers, default_fill)
                a6_02_14 = row[headers.index('a6_02_14')]
                if not (a6_02_14 is None or a6_02_14 == '' or a6_02_14 == '0'):
                    self.print_warning('a6_02_14', i, row, headers, default_fill)
                a6_02_15 = row[headers.index('a6_02_15')]
                if not (a6_02_15 is None or a6_02_15 == '' or a6_02_15 == '0'):
                    self.print_warning('a6_02_15', i, row, headers, default_fill)
                a6_03 = row[headers.index('a6_03')]
                if not (a6_03 is None or a6_03 == ''):
                    self.print_warning('a6_03', i, row, headers, default_fill)
            a6_04 = row[headers.index('a6_04')]
            if a6_04 != '1':
                a6_05 = row[headers.index('a6_05')]
                if not (a6_05 is None or a6_05 == ''):
                    self.print_warning('a6_05', i, row, headers, default_fill)
            a6_05 = row[headers.index('a6_05')]
            if a6_05 != '1' or a6_04 != '1':
                a6_06_1d = row[headers.index('a6_06_1d')]
                if not (a6_06_1d is None or a6_06_1d == ''):
                    self.print_warning('a6_06_1d', i, row, headers, default_fill)
                a6_06_1m = row[headers.index('a6_06_1m')]
                if not (a6_06_1m is None or a6_06_1m == ''):
                    self.print_warning('a6_06_1m', i, row, headers, default_fill)
                a6_06_1y = row[headers.index('a6_06_1y')]
                if not (a6_06_1y is None or a6_06_1y == ''):
                    self.print_warning('a6_06_1y', i, row, headers, default_fill)
                a6_06_2d = row[headers.index('a6_06_2d')]
                if not (a6_06_2d is None or a6_06_2d == ''):
                    self.print_warning('a6_06_2d', i, row, headers, default_fill)
                a6_06_2m = row[headers.index('a6_06_2m')]
                if not (a6_06_2m is None or a6_06_2m == ''):
                    self.print_warning('a6_06_2m', i, row, headers, default_fill)
                a6_06_2y = row[headers.index('a6_06_2y')]
                if not (a6_06_2y is None or a6_06_2y == ''):
                    self.print_warning('a6_06_2y', i, row, headers, default_fill)
                a6_07d = row[headers.index('a6_07d')]
                if not (a6_07d is None or a6_07d == ''):
                    self.print_warning('a6_07d', i, row, headers, default_fill)
                a6_07m = row[headers.index('a6_07m')]
                if not (a6_07m is None or a6_07m == ''):
                    self.print_warning('a6_07m', i, row, headers, default_fill)
                a6_07y = row[headers.index('a6_07y')]
                if not (a6_07y is None or a6_07y == ''):
                    self.print_warning('a6_07y', i, row, headers, default_fill)
                a6_08 = row[headers.index('a6_08')]
                if not (a6_08 is None or a6_08 == ''):
                    self.print_warning('a6_08', i, row, headers, default_fill)
            a6_09 = row[headers.index('a6_09')]
            if a6_09 != '1':
                a6_10 = row[headers.index('a6_10')]
                if not (a6_10 is None or a6_10 == ''):
                    self.print_warning('a6_10', i, row, headers, default_fill)
            a6_10 = row[headers.index('a6_10')]
            if a6_10 != '1' or a6_09 != '1':
                a6_11 = row[headers.index('a6_11')]
                if not (a6_11 is None or a6_11 == ''):
                    self.print_warning('a6_11', i, row, headers, default_fill)
                a6_12 = row[headers.index('a6_12')]
                if not (a6_12 is None or a6_12 == ''):
                    self.print_warning('a6_12', i, row, headers, default_fill)
                a6_13 = row[headers.index('a6_13')]
                if not (a6_13 is None or a6_13 == ''):
                    self.print_warning('a6_13', i, row, headers, default_fill)
                a6_14 = row[headers.index('a6_14')]
                if not (a6_14 is None or a6_14 == ''):
                    self.print_warning('a6_14', i, row, headers, default_fill)
                a6_15 = row[headers.index('a6_15')]
                if not (a6_15 is None or a6_15 == ''):
                    self.print_warning('a6_15', i, row, headers, default_fill)
            g5_02 = row[headers.index('g5_02')]
            if g5_02 != '2':
                a3_01 = row[headers.index('a3_01')]
                if not (a3_01 is None or a3_01 == ''):
                    self.print_warning('a3_01', i, row, headers, default_fill)
                a3_02 = row[headers.index('a3_02')]
                if not (a3_02 is None or a3_02 == ''):
                    self.print_warning('a3_02', i, row, headers, default_fill)
                a3_03 = row[headers.index('a3_03')]
                if not (a3_03 is None or a3_03 == ''):
                    self.print_warning('a3_03', i, row, headers, default_fill)
            a3_03 = row[headers.index('a3_03')]
            if g5_02 != '2' or a3_03 == '1':
                a3_05 = row[headers.index('a3_05')]
                if not (a3_05 is None or a3_05 == '' or a3_05 == '0'):
                    self.print_warning('a3_05', i, row, headers, default_fill)
                a3_06 = row[headers.index('a3_06')]
                if not (a3_06 is None or a3_06 == '' or a3_06 == '0'):
                    self.print_warning('a3_06', i, row, headers, default_fill)
                a3_07 = row[headers.index('a3_07')]
                if not (a3_07 is None or a3_07 == '' or a3_07 == '0'):
                    self.print_warning('a3_07', i, row, headers, default_fill)
                a3_10 = row[headers.index('a3_10')]
                if not (a3_10 is None or a3_10 == '' or a3_10 == '0'):
                    self.print_warning('a3_10', i, row, headers, default_fill)
            a3_07 = row[headers.index('a3_07')]
            # TODO - Verify these questions.
            # changed this per abie email
            if g5_02 != '2' or a3_03 == '1' or a3_07 != '1':
                a3_08a = row[headers.index('a3_08a')]
                if not (a3_08a is None or a3_08a == ''):
                    self.print_warning('a3_08a', i, row, headers, default_fill)
                a3_08b = row[headers.index('a3_08b')]
                if not (a3_08b is None or a3_08b == ''):
                    self.print_warning('a3_08b', i, row, headers, default_fill)
                    # abie.  same for this one?
                a3_09 = row[headers.index('a3_09')]
                if not (a3_09 is None or a3_09 == ''):
                    self.print_warning('a3_09', i, row, headers, default_fill)
            a3_10 = row[headers.index('a3_10')]
            if g5_02 != '2' or a3_03 == '1' or a3_10 != '1':
                a3_11a = row[headers.index('a3_11a')]
                if not (a3_11a is None or a3_11a == ''):
                    self.print_warning('a3_11a', i, row, headers, default_fill)
                a3_11b = row[headers.index('a3_11b')]
                if not (a3_11b is None or a3_11b == ''):
                    self.print_warning('a3_11b', i, row, headers, default_fill)
                a3_12 = row[headers.index('a3_12')]
                if not (a3_12 is None or a3_12 == ''):
                    self.print_warning('a3_12', i, row, headers, default_fill)
            a3_12 = row[headers.index('a3_12')]
            # abie.  same for all?
            if g5_02 != '2' or a3_03 == '1' or a3_10 != '1' or a3_12 == '1':
                a3_13 = row[headers.index('a3_13')]
                if not (a3_13 is None or a3_13 == ''):
                    self.print_warning('a3_13', i, row, headers, default_fill)
                a3_14 = row[headers.index('a3_14')]
                if not (a3_14 is None or a3_14 == ''):
                    self.print_warning('a3_14', i, row, headers, default_fill)
                a3_15 = row[headers.index('a3_15')]
                if not (a3_15 is None or a3_15 == ''):
                    self.print_warning('a3_15', i, row, headers, default_fill)
                a3_16a = row[headers.index('a3_16a')]
                if not (a3_16a is None or a3_16a == ''):
                    self.print_warning('a3_16a', i, row, headers, default_fill)
                a3_16b = row[headers.index('a3_16b')]
                if not (a3_16b is None or a3_16b == ''):
                    self.print_warning('a3_16b', i, row, headers, default_fill)
            a3_15 = row[headers.index('a3_15')]
            if g5_02 != '2' or a3_03 == '1' or a3_12 == '1' or a3_15 == '1':
                a3_17 = row[headers.index('a3_17')]
                if not (a3_17 is None or a3_17 == '' or a3_17 == '0'):
                    self.print_warning('a3_17', i, row, headers, default_fill)
            a3_17 = row[headers.index('a3_17')]
            if g5_02 != '2' or a3_03 == '1' or a3_12 == '1' or a3_15 == '1' or a3_17 == '1':
                a3_18 = row[headers.index('a3_18')]
                if not (a3_18 is None or a3_18 == '' or a3_18 == '0'):
                    self.print_warning('a3_18', i, row, headers, default_fill)
            a3_18 = row[headers.index('a3_18')]
            if (g5_02 != '2' or a3_03 != '0' or a3_15 == '1' or a3_18 != '1') and a3_17 != '1':
                a3_19 = row[headers.index('a3_19')]
                if not (a3_19 is None or a3_19 == ''):
                    self.print_warning('a3_19', i, row, headers, default_fill)
                a3_20 = row[headers.index('a3_20')]
                if not (a3_20 is None or a3_20 == ''):
                    self.print_warning('a3_20', i, row, headers, default_fill)
            if g5_02 != '2' or a3_03 != '1':
                a3_04 = row[headers.index('a3_04')]
                if not (a3_04 is None or a3_04 == ''):
                    self.print_warning('a3_04', i, row, headers, default_fill)

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

        status_logger.debug('Adult :: Analyzing free text')

        if self.short_form:
            for row in matrix:
                if row[headers_old.index('adult_7_1')] == '1':
                    self.process_free_text('kidney', row, headers)
                if row[headers_old.index('adult_7_2')] == '1':
                    self.process_free_text('dialysis', row, headers)
                if row[headers_old.index('adult_7_3')] == '1':
                    self.process_free_text('fever', row, headers)
                if row[headers_old.index('adult_7_4')] == '1':
                    self.process_free_text('ami', row, headers)
                if row[headers_old.index('adult_7_5')] == '1':
                    self.process_free_text('heart', row, headers)
                if row[headers_old.index('adult_7_6')] == '1':
                    self.process_free_text('jaundice', row, headers)
                if row[headers_old.index('adult_7_7')] == '1':
                    self.process_free_text('liver', row, headers)
                if row[headers_old.index('adult_7_8')] == '1':
                    self.process_free_text('malaria', row, headers)
                if row[headers_old.index('adult_7_9')] == '1':
                    self.process_free_text('pneumonia', row, headers)
                if row[headers_old.index('adult_7_10')] == '1':
                    self.process_free_text('renal', row, headers)
                if row[headers_old.index('adult_7_11')] == '1':
                    self.process_free_text('suicide', row, headers)

        free_text = ['a5_01_9b', 'a6_08', 'a6_11', 'a6_12', 'a6_13', 'a6_14', 'a6_15', 'a7_01']

        # we've already lowercased and removed numbers at this point
        for question in free_text:
            index = headers.index(question)
            for row in matrix:
                answer = row[index]
                self.process_free_text(answer, row, headers)

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

    @staticmethod
    def process_free_text(answer, row, headers):
        key_words = ADULT_WORDS_TO_VARS.keys()
        answer_array = answer.split(' ')
        for word in answer_array:
            for keyword in key_words:
                stemmed = stem(word)
                if stemmed == keyword:
                    s_var = ADULT_WORDS_TO_VARS[keyword]
                    s_index = headers.index(s_var)
                    row[s_index] = '1'

    def print_warning(self, var, row_num, row, headers, default_fill):
        warning_logger.warning('Adult :: Value at row {} col {} for variable {} should be blank, setting to default and continuing'.format(row_num + 2, headers.index(var), var))
        row[headers.index(var)] = str(default_fill.get(var))
        self.warnings = True
