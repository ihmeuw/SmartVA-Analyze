import abc
import csv
import os

from smartva.loggers import warning_logger
from smartva.utils.conversion_utils import convert_binary_variable, ConversionError
from smartva.utils import intermediate_dir_path


class AbortException(Exception):
    pass


class Prep(object):
    __metaclass__ = abc.ABCMeta

    INPUT_FILENAME_TEMPLATE = ''
    OUTPUT_FILENAME_TEMPLATE = ''

    def __init__(self, working_dir_path):
        self.working_dir_path = working_dir_path
        self.input_dir_path = working_dir_path
        self.output_dir_path = working_dir_path

        self.want_abort = False

    def check_abort(self):
        if self.want_abort:
            raise AbortException()

    def run(self):
        self.check_abort()

    def abort(self):
        self.want_abort = True


class DataPrep(Prep):
    __metaclass__ = abc.ABCMeta

    AGE_GROUP = None

    def __init__(self, working_dir_path, short_form):
        super(DataPrep, self).__init__(working_dir_path)
        self.short_form = short_form

    def input_file_path(self, age_group=None, filename_template=None):
        template = filename_template or self.INPUT_FILENAME_TEMPLATE
        age_group = age_group or self.AGE_GROUP
        return os.path.join(self.input_dir_path, template.format(age_group))

    def output_file_path(self, age_group=None, filename_template=None):
        template = filename_template or self.OUTPUT_FILENAME_TEMPLATE
        age_group = age_group or self.AGE_GROUP
        return os.path.join(self.output_dir_path, template.format(age_group))

    @property
    def intermediate_dir(self):
        return intermediate_dir_path(self.working_dir_path)

    def pre_processing_step(self, row):
        """Pipeline specific pre-processing actions.

        Args:
            row: Row of VA data.
        """
        pass

    def post_processing_step(self, row):
        """Pipeline specific post-processing actions.

        Args:
            row: Row of VA data.
        """
        pass

    @staticmethod
    def rename_vars(row, conversion_map):
        for old_header, new_header in conversion_map.items():
            try:
                row[new_header] = row.pop(old_header)
            except KeyError:
                warning_logger.warning(
                    'SID: {} variable \'{}\' does not exist and cannot be renamed to \'{}\'.'
                    .format(row['sid'], old_header, new_header))

    @staticmethod
    def rename_headers(headers, conversion_map):
        """
        Rename headers to match the next processing step.

        :param headers: List of headers.
        :param conversion_map: Map of old to new headers.
        """
        for old_header, new_header in conversion_map.items():
            try:
                headers[headers.index(old_header)] = new_header
            except (KeyError, ValueError):
                pass  # Header did not exist.

    @staticmethod
    def drop_from_list(item_list, drop_index_list):
        """
        Return a pruned list.

        :param item_list: List of items to prune.
        :param drop_index_list: Indices to prune.
        :return: New list of items.
        """
        # Return a new list of headers containing all but the items in the drop list.
        return [item for index, item in enumerate(item_list) if index not in drop_index_list]

    @staticmethod
    def process_binary_vars(row, conversion_map):
        """
        Convert multiple value answers into binary cells.

        :param row: Row of data.
        :param conversion_map: Data structure with header and binary variable mapping.
        """
        for data_header, data_map in conversion_map:
            try:
                convert_binary_variable(row, data_header, data_map)
            except ConversionError as e:
                warning_logger.debug(e.message)
                continue
            except KeyError as e:
                # Variable does not exist. The new published form does not contain all of the previous variables.
                warning_logger.debug('SID: {} variable \'{}\' does not exist. process_binary_vars'
                                     .format(row['sid'], e.message))
                continue

    @staticmethod
    def expand_row(row, data):
        dupes = set(row.keys()) & set(data.keys())
        if len(dupes):
            # warning_logger.warning('')
            pass
        row.update({k: v for k, v in data.items() if k not in row})

    @staticmethod
    def process_progressive_value_data(row, progressive_data):
        """
        Populate progressive variables from input data.
        Format:
        {
            'read variable': [
                (upper, variable),
                (median, variable),
                (lower, variable),
                (0, variable)
            ]
        }

        :param row: Row of data.
        :param progressive_data: Quartile ranges in specified format.
        """
        for read_header, conversion_data in progressive_data:
            for value, write_header in conversion_data:
                if float(row[read_header]) > value:
                    if isinstance(write_header, tuple):
                        write_header, write_value = write_header
                    else:
                        write_value = 1
                    row[write_header] = write_value
                    break

    @staticmethod
    def read_input_file(input_file_path, mode='rb'):
        """Read input file. Return headers and matrix data.

        Args:
            input_file_path (str): Input file path.
            mode (str): Read mode.

        Returns:
            list, list: List of headers, List of matrix data.
        """
        with open(input_file_path, mode) as fi:
            reader = csv.DictReader(fi)
            return reader.fieldnames, [row for row in reader]

    @staticmethod
    def write_output_file(headers, matrix, output_file_path):
        """Write output file.

        Args:
            headers (list): List of headers to be retained.
            matrix (list): Matrix of VA answers.
            output_file_path (str): Path of output file.
        """
        with open(output_file_path, 'wb') as fo:
            writer = csv.DictWriter(fo, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matrix)
