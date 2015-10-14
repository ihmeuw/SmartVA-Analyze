import csv
import os

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier, get_item_count
from smartva.adult_symptom_data import (
    GENERATED_HEADERS,
    ADULT_CONVERSION_VARIABLES,
    COPY_VARIABLES,
    AGE_QUARTILE_BINARY_VARIABLES,
    DURATION_CUTOFF_DATA,
    INJURY_VARIABLES,
    BINARY_VARIABLES,
    FREE_TEXT_VARIABLES,
    DROP_LIST,
    BINARY_CONVERSION_MAP
)
from smartva.utils.conversion_utils import additional_headers_and_values

FILENAME_TEMPLATE = '{:s}-symptom.csv'


class AdultSymptomPrep(DataPrep):
    """
    Prepare symptom data for tariff processing.

    The main goal of this step is to complete the conversion of symptom answers to binary data.

    Notes:
    Change sex from female = 2, male = 1 to female = 1, male = 0
    Unknown sex will default to 0 so it contributes nothing to the tariff score as calculated in the
    tariff 2.0 algorithm.

    For all indicators for different questions about injuries (road traffic, fall, fires) We only want
    to give a VA a 1 (yes) response for that question if the injury occurred within 30 days of death
    (i.e. s163<=30) Otherwise, we could have people who responded that they were in a car accident 20
    years prior to death be assigned to road traffic deaths.
    """
    AGE_GROUP = 'adult'

    def run(self):
        status_logger.info('Adult :: Processing Adult symptom data')
        status_notifier.update({'progress': (3,)})

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.writer(fo)

            with open(self.input_file_path, 'rb') as fi:
                reader = csv.reader(fi)
                records = get_item_count(reader, fi) - 1
                status_notifier.update({'sub_progress': (0, records)})

                headers = next(reader)

                additional_headers, additional_values = additional_headers_and_values(headers, GENERATED_HEADERS)

                headers.extend(additional_headers)

                self.rename_headers(headers, ADULT_CONVERSION_VARIABLES)

                # Identify unneeded variables for removal, and write the new headers to the output file.
                not_drop_list = ADULT_CONVERSION_VARIABLES.values() + FREE_TEXT_VARIABLES + additional_headers

                drop_index_list = set([i for i, header in enumerate(headers) if header not in not_drop_list])
                drop_index_list.update([headers.index(header) for header in DROP_LIST])

                writer.writerow(self.drop_from_list(headers, drop_index_list))

                for index, row in enumerate(reader):
                    if self.want_abort:
                        return False

                    status_notifier.update({'sub_progress': (index,)})

                    new_row = row + additional_values

                    self.copy_variables(headers, new_row, COPY_VARIABLES)

                    # Compute age quartiles.
                    self.process_quartile_data(headers, new_row, AGE_QUARTILE_BINARY_VARIABLES.items())

                    self.process_cutoff_data(headers, new_row, DURATION_CUTOFF_DATA.items())

                    self.process_injury_data(headers, new_row, INJURY_VARIABLES.items())

                    # Dichotomize!
                    self.process_binary_variables(headers, new_row, BINARY_CONVERSION_MAP.items())

                    # Ensure all binary variables actually ARE 0 or 1:
                    self.post_process_binary_variables(headers, new_row, BINARY_VARIABLES)

                    writer.writerow(self.drop_from_list(new_row, drop_index_list))

        status_notifier.update({'sub_progress': None})

        return True

    @staticmethod
    def copy_variables(headers, row, copy_variables_map):
        """
        Copy data from one variable to another.
        {
            'read variable': 'write variable'
        }

        :param headers: List of headers.
        :param row: Row of data.
        :param copy_variables_map: Dict of read header and write header.
        """
        for read_header, write_header in copy_variables_map.items():
            row[headers.index(write_header)] = row[headers.index(read_header)]

    @staticmethod
    def process_quartile_data(headers, row, quartile_data):
        """
        Populate quartile variables from input data.
        Format:
        {
            'read variable': [
                (upper, variable),
                (median, variable),
                (lower, variable),
                (0, variable)
            ]
        }

        :param headers: List of headers.
        :param row: Row of data.
        :param quartile_data: Quartile ranges in specified format.
        """
        for read_header, conversion_data in quartile_data:
            for value, write_header in conversion_data:
                if int(row[headers.index(read_header)]) > value:
                    row[headers.index(write_header)] = 1
                    break

    @staticmethod
    def process_cutoff_data(headers, row, cutoff_data_map):
        """
        Change read variable to 1/0 if value is greater/less or equeal to cutoff, respectively.
        Format:
        {
            variable: cutoff
        }

        :param headers:
        :param row:
        :param cutoff_data_map: Dict in specified format.
        """
        for read_header, cutoff_data in cutoff_data_map:
            try:
                row[headers.index(read_header)] = int(float(row[headers.index(read_header)]) >= cutoff_data)
            except ValueError:
                row[headers.index(read_header)] = 0

    @staticmethod
    def process_injury_data(headers, row, injury_variable_map):
        """
        If injury occurred more than 30 days from death, set variable to 0.
        Format:
        {
            'read variable': [list of injury variables]
        }

        :param headers: List of headers.
        :param row: Row of data.
        :param injury_variable_map: Dict in specified format.
        """
        for read_header, injury_list in injury_variable_map:
            if float(row[headers.index(read_header)]) > 30:
                for injury in injury_list:
                    row[headers.index(injury)] = 0

    @staticmethod
    def post_process_binary_variables(headers, row, binary_variables):
        """
        Ensure all binary variables are actually 1 or 0.
        Format:
            [list of binary variables]

        :param headers: List of headers.
        :param row: Row of data.
        :param binary_variables: List in specified format.
        """
        for read_header in binary_variables:
            try:
                value = int(row[headers.index(read_header)])
            except ValueError:
                value = 0
            row[headers.index(read_header)] = int(value == 1)

    def abort(self):
        self.want_abort = True
