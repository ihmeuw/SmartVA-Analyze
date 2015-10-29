from smartva.utils import LdapNotationParser
from smartva.loggers import warning_logger


class ConversionError(Exception):
    pass


def value_or_default(x, fn=int, invalid=None, default=0):
    try:
        value = fn(x)
        if value not in (invalid if isinstance(invalid, list) else [invalid]):
            return value
    except ValueError:
        pass
    return default


def additional_headers_and_values(headers, additional_headers_data):
    """
    Calculate necessary additional headers and values based on comparing existing headers to additional header data.

    :param headers:
    :return:
    """
    additional_headers = []
    additional_values = []
    dupe_headers = []
    for k, v in additional_headers_data:
        if k not in headers:
            additional_headers.append(k)
            additional_values.append(v)
        else:
            dupe_headers.append(k)

    if dupe_headers:
        warning_logger.warning(
            'Headers in list {} already exist in input file and were not added.'.format(dupe_headers))
    return additional_headers, additional_values


def get_header_index(headers, header):
    try:
        return headers.index(header)
    except ValueError:
        raise ConversionError('Skipping missing header \'{}\'.'.format(header))


def convert_binary_variable(row, data_header, data_map):
    """
    Convert multiple value answers into binary cells.

    :param row: Data from a single report.
    :param data_header: Header of column containing parsable data.
    :param data_map: Map of the values to binary value headers
    """
    # index = row[data_header]
    try:
        for value in map(int, str(row[data_header]).split(' ')):
            if isinstance(data_map, dict):
                if value in data_map:
                    row[data_map[value]] = 1
            elif isinstance(data_map, list):
                row[data_header] = int(value in data_map)

    except ValueError:
        # No values to process or not an integer value (invalid).
        pass


def check_skip_patterns(row, skip_pattern_data, default_values=None):
    def get_cell(var):
        value = row[var]
        try:
            return int(value)
        except ValueError:
            return 0

    default_values = default_values or {}

    warnings = False
    for skip_pattern_item in skip_pattern_data:
        skip_condition, skip_list = skip_pattern_item
        if not LdapNotationParser(skip_condition, get_cell, int).parse():
            for skip_list_item in skip_list:
                skip_list_item_value = get_cell(skip_list_item)
                if bool(skip_list_item_value):
                    warnings = True
                    warning_logger.info('SID: {} variable {} has value {}, but should be blank.'
                                        .format(row['sid'], skip_list_item, skip_list_item_value))
                    row[skip_list_item] = default_values.get(skip_list_item, 0)

    return warnings
