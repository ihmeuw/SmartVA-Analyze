import csv
import os
import threading


def intermediate_dir_path(output_dir_path):
    return os.path.join(output_dir_path, 'intermediate-files')


def shorten_path(path, max_length):
    if len(path) <= max_length:
        return path

    return path[:int(max_length * .25)] + '...' + path[-int(max_length * .75):]


def synchronized(fn):
    def fn_wrap(self, *args, **kwargs):
        with self.mutex:
            fn(self, *args, **kwargs)

    return fn_wrap


class StatusNotifier(object):
    def __init__(self):
        self.mutex = threading.RLock()
        self._handlers = set()

    @synchronized
    def register(self, handler):
        self._handlers.add(handler)

    @synchronized
    def unregister(self, handler):
        self._handlers.remove(handler)

    @synchronized
    def notify(self, data):
        for handler in self._handlers:
            handler(data)

    def update(self, data):
        self.notify(data)


status_notifier = StatusNotifier()


def find_dupes(items):
    dupe_items = []
    for item in items:
        if item and item not in dupe_items:
            if items.count(item) > 1:
                dupe_items.append(item)
    return dupe_items


def get_item_count(items, f=None):
    """
    Use this to get a count of items in a collection that doesn't support len(), like a file reader.
    Due to the internal workings of readers, this must be done prior to any reader operations.

    :param items: Object containing the items.
    :param f: File to reset seek index.
    :return: Count of items.
    """
    count = 0
    for _ in items:
        count += 1
    if f:
        try:
            f.seek(0)
        except AttributeError:
            pass
    return count


def get_item_count_for_file(f):
    reader = csv.reader(f)
    count = 0
    for _ in reader:
        count += 1
    f.seek(0)
    return count


def int_or_float(x):
    """Return int or float value of x.

    Args:
        x (str): Value to convert.

    Returns:
        int or float:

    Raises:
        ValueError:
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            raise ValueError('invalid literal for int_or_float(): \'{}\''.format(x))


def identity(arg):
    return arg


def value_from_row(row, fn=identity, default=None):
    def fn_wrap(var):
        try:
            return fn(row[var])
        except Exception:  # unknown function can raise unpredictable exception
            return default

    return fn_wrap
