import csv
import os

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier
from smartva.utils.conversion_utils import additional_headers_and_values

FILENAME_TEMPLATE = '{:s}-symptom.csv'


class SymptomPrep(DataPrep):
    def __init__(self, input_file, output_dir, short_form):
        super(SymptomPrep, self).__init__(input_file, output_dir, short_form)
        self.data_module = None

    def _init_data_module(self):
        pass

    def run(self):
        super(SymptomPrep, self).run()
        status_logger.info('{} :: Processing symptom data'.format(self.AGE_GROUP.capitalize()))
        status_notifier.update({'progress': 1})

        with open(self.input_file_path, 'rb') as fi:
            reader = csv.DictReader(fi)
            matrix = [row for row in reader]

        status_notifier.update({'sub_progress': (0, len(matrix))})

        headers = reader.fieldnames

        additional_data = {}
        additional_data.update(self.data_module.GENERATED_VARS_DATA)
        additional_headers, additional_values = additional_headers_and_values(headers, additional_data.items())

        headers.extend(additional_headers)
        self.rename_headers(headers, self.data_module.VAR_CONVERSION_MAP)

        # TODO - Review this and re-implement for DictWriter, if necessary.
        # Identify unneeded variables for removal, and write the new headers to the output file.
        """
        not_drop_list = VAR_CONVERSION_MAP.values() + FREE_TEXT_VARIABLES + additional_headers

        drop_index_list = set([i for i, header in enumerate(headers) if header not in not_drop_list])
        drop_index_list.update([headers.index(header) for header in DROP_LIST])
        """

        for index, row in enumerate(matrix):
            if self.want_abort:
                return False

            status_notifier.update({'sub_progress': (index,)})

            self.expand_row(row, dict(zip(additional_headers, additional_values)))
            self.rename_vars(row, self.data_module.VAR_CONVERSION_MAP)

            self.copy_variables(row, self.data_module.COPY_VARS)

            # Compute age quartiles.
            self.process_progressive_value_data(row, self.data_module.AGE_QUARTILE_BINARY_VARS.items())

            self.process_cutoff_data(row, self.data_module.DURATION_CUTOFF_DATA.items())

            self.process_injury_data(row, self.data_module.INJURY_VARS.items())

            # Dichotomize!
            self.process_binary_vars(row, self.data_module.BINARY_CONVERSION_MAP.items())

            # Ensure all binary variables actually ARE 0 or 1:
            self.post_process_binary_variables(row, self.data_module.BINARY_VARS)

        status_notifier.update({'sub_progress': None})

        self.write_output_file(headers, matrix)

        return True

    @staticmethod
    def copy_variables(row, copy_variables_map):
        """
        Copy data from one variable to another.
        {
            'read variable': 'write variable'
        }

        :param row: Row of data.
        :param copy_variables_map: Dict of read header and write header.
        """
        for read_header, write_header in copy_variables_map.items():
            row[write_header] = row[read_header]

    @staticmethod
    def process_cutoff_data(row, cutoff_data_map):
        """
        Change read variable to 1/0 if value is greater/less or equal to cutoff, respectively.
        Format:
        {
            variable: cutoff
        }

        :param row:
        :param cutoff_data_map: Dict in specified format.
        """
        for read_header, cutoff_data in cutoff_data_map:
            try:
                row[read_header] = int(float(row[read_header]) >= cutoff_data)
            except ValueError:
                row[read_header] = 0

    @staticmethod
    def process_injury_data(row, injury_variable_map):
        """
        If injury occurred more than 30 days from death, set variable to 0.
        Format:
        {
            'read variable': [list of injury variables]
        }

        :param row: Row of data.
        :param injury_variable_map: Dict in specified format.
        """
        for read_data, injury_list in injury_variable_map:
            read_header, cutoff = read_data
            if float(row[read_header]) > cutoff:
                for injury in injury_list:
                    row[injury] = 0

    @staticmethod
    def post_process_binary_variables(row, binary_variables):
        """
        Ensure all binary variables are actually 1 or 0.
        Format:
            [list of binary variables]

        :param row: Row of data.
        :param binary_variables: List in specified format.
        """
        for read_header in binary_variables:
            try:
                value = int(row[read_header])
            except ValueError:
                value = 0
            row[read_header] = int(value == 1)

    def write_output_file(self, headers, matrix):
        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.DictWriter(fo, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matrix)
