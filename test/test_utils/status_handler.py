from __future__ import print_function

"""Test utility to output status messages and progress.
usage: status_notifier.register(StatusHandler())
run pytest with flag '-s' to see output.
"""


class StatusHandler(object):
    def __init__(self):
        self.high_value = 0

    def __call__(self, data):
        if 'label' in data:
            print(data['label'])

        if 'message' in data:
            print(data['message'])

        if 'sub_progress' in data:
            if not data['sub_progress']:
                self.high_value = 0
                print()

            elif len(data['sub_progress']) > 1:
                print()
                self.high_value = data['sub_progress'][1]

            elif self.high_value and data['sub_progress'][0] % ((self.high_value / 10) or 1) == 0:
                print('..{}'.format(data['sub_progress'][0] * 100 / self.high_value))
