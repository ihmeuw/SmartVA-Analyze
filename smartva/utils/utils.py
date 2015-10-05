import csv
import os
import re
import threading


def shorten_path(path, maxLength):
    pathLength = 0
    pathLengthMax = maxLength
    shortenedPathList = []

    # split path into list
    splitPathList = path.split(os.path.sep)

    # start from end and iterate through each path element,
    for pathItem in reversed(splitPathList):
        # sum the length of the path so far
        pathLength += len(pathItem)
        # if less than max
        if pathLength <= pathLengthMax:
            # create shorted path
            shortenedPathList.append(pathItem)
        else:
            # no need to go through the loop
            break

    # reverse the shortened path, convert to a string
    shortenedPathList.reverse()
    shortenedPath = os.path.sep.join(shortenedPathList)
    # for shorter path, add ...
    if shortenedPath.startswith(os.path.sep) or re.match('[A-Z]:', shortenedPath):
        return shortenedPath
    else:
        return '..' + os.path.sep + shortenedPath


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


def get_item_count(items, f=None):
    """
    Use this to get a count of items in a collection that doesn't support len(), like a file reader.
    Due to the internal workings of readers, this must be done prior to any reader operations.

    :param items: Object containing the items.
    :param f: File to reset seek index.
    :return: Count of items.
    """
    count = 0
    for count, _ in enumerate(items):
        pass
    if f:
        try:
            f.seek(0)
        except AttributeError:
            pass
    return count
