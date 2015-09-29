class ConversionError(Exception):
    pass


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
    for value in str(row[index]).split(' '):
        try:
            if int(value) in data_map:
                row[headers.index(data_map[int(value)])] = 1
        except ValueError:
            # No values to process or not an integer value (invalid).
            pass
