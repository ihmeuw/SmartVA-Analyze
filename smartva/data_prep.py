from smartva.loggers import warning_logger
from smartva.utils.conversion_utils import convert_binary_variable, ConversionError


class DataPrep(object):
    AGE_GROUP = 'none'

    def __init__(self, input_file, output_dir, short_form):
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.short_form = short_form

        self.want_abort = False

    def run(self):
        pass

    def abort(self):
        self.want_abort = True

    @staticmethod
    def rename_vars(row, conversion_map):
        for old_header, new_header in conversion_map.items():
            try:
                row[new_header] = row.pop(old_header)
            except KeyError:
                warning_logger.warning(
                    'Variable \'{}\' does not exist and cannot be renamed to \'{}\'.'.format(old_header, new_header))

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

    @staticmethod
    def expand_row(row, data):
        dupes = set(row.keys()) & set(data.keys())
        if len(dupes):
            # warning_logger.warning('')
            pass
        row.update({k: v for k, v in data.items() if k not in row})
