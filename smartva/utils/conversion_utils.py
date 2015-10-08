from smartva.utils import LdapNotationParser
from smartva.loggers import warning_logger


class ConversionError(Exception):
    pass


def int_value_or_0(x):
    try:
        return int(x)
    except ValueError:
        return 0


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
        else:
            warning_logger.warning('Header "{}" already exists in data set and was not added.'.format(k))

    return additional_headers, additional_values


def get_header_index(headers, header):
    try:
        return headers.index(header)
    except ValueError:
        raise ConversionError('Skipping missing header "{}".'.format(header))


def convert_binary_variable(headers, row, data_header, data_map):
    """
    Convert multiple value answers into binary cells.

    :param headers: List of headers to provide cell index.
    :param row: Data from a single report.
    :param data_header: Header of column containing parsable data.
    :param data_map: Map of the values to binary value headers
    """
    index = get_header_index(headers, data_header)
    try:
        for value in map(int, str(row[index]).split(' ')):
            if isinstance(data_map, dict):
                if value in data_map:
                    row[headers.index(data_map[value])] = 1
            elif isinstance(data_map, list):
                row[index] = int(value in data_map)

    except ValueError:
        # No values to process or not an integer value (invalid).
        pass


def check_skip_patterns(headers, row, skip_pattern_data):
    def get_cell(header):
        value = row[headers.index(header)]
        try:
            return int(value)
        except ValueError:
            return 0

    warnings = False
    for skip_pattern_item in skip_pattern_data:
        skip_condition, skip_list = skip_pattern_item
        if not LdapNotationParser(skip_condition, get_cell, int).parse():
            for skip_list_item in skip_list:
                skip_list_item_value = get_cell(skip_list_item)
                if bool(skip_list_item_value):
                    warnings = True
                    warning_logger.info('SID: {} variable {} has value {}, but should be blank.'
                                        .format(row[headers.index('sid')], skip_list_item, skip_list_item_value))
                    row[headers.index(skip_list_item)] = 0

    return warnings
