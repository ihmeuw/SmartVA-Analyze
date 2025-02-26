from smartva.utils import LdapNotationParser
from smartva.loggers import warning_logger


class ConversionError(Exception):
    pass


def value_or_default(x, fn=int, invalid=None, default=0):
    try:
        value = fn(x)
        if value not in (invalid if isinstance(invalid, list) else [invalid]):
            return value
    except (TypeError, ValueError):
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


def get_cell(row):
    def fn(var):
        try:
            return int(row[var])
        except (KeyError, ValueError):
            # Variable doesn't exist or is not valid. This is OK.
            pass
        return 0

    return fn


def safe_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return 0.0


def safe_int(x):
    return int(safe_float(x))