from __future__ import print_function

"""Test utility to output status messages and progress.
usage: status_notifier.register(StatusHandler())
run pytest with flag '-s' to see output.
"""


def _handle_progress(gauge, data):
    if data is None:
        gauge['value'] = 0
        return '0..0'

    elif isinstance(data, int):
        gauge['value'] += data
        return '{}..{}'.format(gauge['value'], gauge['max'])

    elif isinstance(data, (list, set, tuple)):
        gauge['value'] = data[0]

        if len(data) > 1:
            gauge['max'] = data[1]
            return '0..{}'.format(gauge['max'])

        elif gauge['max'] and data[0] % ((gauge['max'] / 10) or 1) == 0:
            return '{}..{}'.format(gauge['value'], gauge['max'])

    return None


class StatusHandler(object):
    def __init__(self, fn=print):
        self.progress = {'value': 0, 'max': 0}
        self.sub_progress = {'value': 0, 'max': 0}
        self.fn = fn

    def __call__(self, data):
        if 'label' in data:
            self.fn(data['label'])

        if 'message' in data:
            self.fn(data['message'])

        if 'progress' in data:
            progress_str = _handle_progress(self.progress, data['progress'])
            if progress_str is not None:
                self.fn('[{}]'.format(progress_str))

        if 'sub_progress' in data:
            progress_str = _handle_progress(self.sub_progress, data['sub_progress'])
            if progress_str is not None:
                self.fn('{}'.format(progress_str))
