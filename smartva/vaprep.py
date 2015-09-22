import csv
import re
import os

from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from vaprep_data import (
    ADDITIONAL_HEADERS,
    SHORT_FORM_ADDITIONAL_HEADERS_DATA,
    BINARY_CONVERSION_MAP,
    AGE_HEADERS,
    ADULT_RASH_HEADER,
    ADULT_RASH_CONVERSION_HEADERS,
    ADULT_RASH_EVERYWHERE_LIST,
    ADULT_RASH_EVERYWHERE_VALUE,
    CHILD_WEIGHT_CONVERSION_DATA,
    FREE_TEXT_HEADERS,
    WORD_SUBS
)

NEONATE_PREPPED_FILENAME = 'neonate-prepped.csv'
CHILD_PREPPED_FILENAME = 'child-prepped.csv'
ADULT_PREPPED_FILENAME = 'adult-prepped.csv'


def int_value(x):
    try:
        return int(x)
    except ValueError:
        return 0


class VaPrep(object):
    """
    This file cleans up input and converts from ODK collected data to VA variables.
    """

    def __init__(self, input_file, output_dir, short_form):
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.want_abort = 0
        self.short_form = short_form

    @staticmethod
    def additional_headers_and_values(headers):
        additional_headers = ADDITIONAL_HEADERS
        additional_values = [0] * len(ADDITIONAL_HEADERS)
        for k, v in SHORT_FORM_ADDITIONAL_HEADERS_DATA:
            if k not in headers:
                additional_headers.append(k)
                additional_values.append(v)

        return additional_headers, additional_values

    def run(self):
        status_notifier.update({'progress': (1,)})

        status_logger.debug('Initial data prep')

        # matrix is a list of lists containing all of our data
        matrix = list()

        with open(self.input_file_path, 'rU') as f:
            reader = csv.reader(f)

            # Read headers and check for free text columns
            headers = next(reader)

            # Extend the headers with additional headers and read the remaining data into the matrix
            additional_headers, additional_values = self.additional_headers_and_values(headers)
            headers.extend(additional_headers)

            for row in reader:
                matrix.extend([row + additional_values])

        # loop through each row, updating values (mostly additionalHeaders), based on user's answers
        for row in matrix:
            # Fill in blank values for age.
            # TODO: Eliminate this step.
            for header in AGE_HEADERS:
                row[headers.index(header)] = int_value(row[headers.index(header)])

            for header in BINARY_CONVERSION_MAP:
                mapping = BINARY_CONVERSION_MAP[header]
                try:
                    index = headers.index(header)
                except ValueError:
                    # Header does not exist. Log a warning.
                    warning_logger.debug('Skipping missing header "{}".'.format(header))
                else:
                    for value in row[index].split(' '):
                        try:
                            if int(value) in mapping:
                                row[headers.index(mapping[int(value)])] |= 1
                        except ValueError:
                            # No values to process or not an integer value (invalid).
                            pass

            # set adultrash variables based on multiple choice question
            index = headers.index(ADULT_RASH_HEADER)
            try:
                rash_values = list(map(int, row[index].split(' ')))
            except ValueError:
                # No rash data. Skip.
                pass
            else:
                if set(ADULT_RASH_EVERYWHERE_LIST).issubset(set(rash_values)):
                    # if 1, 2, and 3 are selected, then change the value to 4 (all)
                    rash_values = [ADULT_RASH_EVERYWHERE_VALUE]
                # set adultrash to the other selected values
                for rash_index in range(min(len(rash_values), len(ADULT_RASH_CONVERSION_HEADERS))):
                    row[headers.index(ADULT_RASH_CONVERSION_HEADERS[rash_index])] = rash_values[rash_index]

            # Convert weights from kg to g
            for header in CHILD_WEIGHT_CONVERSION_DATA:
                mapping = CHILD_WEIGHT_CONVERSION_DATA[header]
                try:
                    units = int(row[headers.index(header)])
                except ValueError:
                    # No weight data. Skip.
                    pass
                else:
                    if units == 2:
                        weight = float(row[headers.index(mapping[units])]) * 1000
                        row[headers.index(header)] = 1
                        row[headers.index(mapping[1])] = weight

            # this just does a substitution of words in the above list (mostly misspellings, etc..)
            for question in FREE_TEXT_HEADERS:
                try:
                    index = headers.index(question)
                except ValueError:
                    warning_logger.debug('Free text column "{}" does not exist.'.format(question))
                else:
                    # check to see if any of the keys exist in the freetext (keys can be multiple words like 'dog bite')
                    new_answer_array = []
                    for word in re.sub('[^a-z ]', '', row[index].lower()).split(' '):
                        if word in WORD_SUBS:
                            new_answer_array.append(WORD_SUBS[word])
                        elif word:
                            new_answer_array.append(word)

                    row[index] = ' '.join(new_answer_array)

        self.write_data(headers, matrix)

        return 1

    def write_data(self, headers, matrix):
        status_logger.debug('Writing adult, child, neonate prepped.csv files')

        adult_file = open(os.path.join(self.output_dir, ADULT_PREPPED_FILENAME), 'wb', buffering=0)
        child_file = open(os.path.join(self.output_dir, CHILD_PREPPED_FILENAME), 'wb', buffering=0)
        neonate_file = open(os.path.join(self.output_dir, NEONATE_PREPPED_FILENAME), 'wb', buffering=0)

        adult_writer = csv.writer(adult_file)
        child_writer = csv.writer(child_file)
        neonate_writer = csv.writer(neonate_file)

        # write out header files
        adult_writer.writerow(headers)
        child_writer.writerow(headers)
        neonate_writer.writerow(headers)

        # write out data by row into appropriate age range (adult, child, neonate)
        # blank values have already been replaced with 0 (int) here
        for row in matrix:
            years = int(row[headers.index(AGE_HEADERS[0])])
            months = int(row[headers.index(AGE_HEADERS[1])])
            days = int(row[headers.index(AGE_HEADERS[2])])

            if years == 0 and days == 0 and months == 0:
                module = row[headers.index('gen_5_4d')]
                if module == '1':
                    # print 'neonate because gen_5_4d == 1'
                    neonate_writer.writerow(row)
                elif module == '2':
                    # print 'child because gen_5_4d == 2'
                    child_writer.writerow(row)
                elif module == '3':
                    # print 'adult because gen_5_4d == 3'
                    adult_writer.writerow(row)
                else:
                    # print 'neonate because no value for age'
                    updatestr = 'SID: %s has no values for age, defaulting to neonate' % row[headers.index('sid')]
                    warning_logger.warning(updatestr)
                    neonate_writer.writerow(row)
            else:
                if years >= 12:
                    # print 'adult because age >= 12'
                    adult_writer.writerow(row)
                else:
                    if days <= 28 and months == 0 and years == 0:
                        # print 'neonage because age <= 28'
                        neonate_writer.writerow(row)
                    else:
                        # print 'child because nothing else'
                        child_writer.writerow(row)

        adult_file.close()
        child_file.close()
        neonate_file.close()

    def abort(self):
        self.want_abort = 1
