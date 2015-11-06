import click
import logging
import signal
import sys

from progressbar import ProgressBar, Bar, Percentage, ETA

from smartva import prog_name, version
from smartva import workerthread
from smartva.countries import COUNTRIES, COUNTRY_DEFAULT
from smartva.loggers import status_logger
from smartva.utils import status_notifier

worker = None


def configure_logger():
    console_handler = logging.StreamHandler()
    status_logger.addHandler(console_handler)


def check_country(ctx, param, value):
    """
    Check that the specified country is in the list of valid countries. If not, print out a list of valid countries.
    """
    if value.upper() == COUNTRY_DEFAULT.upper():
        return None
    elif not value.upper() in (country.split(u' ')[-1].strip(u'()').upper() for country in COUNTRIES):
        click.echo(u'Country list:')
        for country in COUNTRIES:
            click.echo(u'- {}'.format(country))
        ctx.exit()
    return value.upper()


@click.command()
@click.option('--country', default=COUNTRY_DEFAULT, callback=check_country,
              help='Data origin country abbreviation. "LIST" displays all. Default is "{}".'.format(COUNTRY_DEFAULT))
@click.option('--malaria', default=True, type=click.BOOL, help='Data is a from Malaria region.')
@click.option('--hce', default=True, type=click.BOOL, help='Use Health Care Experience (HCE) variables.')
@click.option('--freetext', default=True, type=click.BOOL, help='Use "free text" variables.')
@click.version_option(version=version, prog_name=prog_name)
@click.argument('input', type=click.Path(file_okay=True, dir_okay=False, readable=True, exists=True))
@click.argument('output', type=click.Path(file_okay=False, dir_okay=True, writable=True, exists=True))
# @click.option('--config', help='Specify options in a YAML file.')
# @click.option('--about', help='About this application.)
def main(*args, **kwargs):
    configure_logger()

    status_logger.info('')
    status_logger.info('Starting analysis with options:')
    status_logger.info('- Input file: {}'.format(kwargs['input']))
    status_logger.info('- Output folder: {}'.format(kwargs['output']))
    status_logger.info('- Country: {}'.format(kwargs['country']))
    status_logger.info('- Malaria Region: {}'.format(kwargs['malaria']))
    status_logger.info('- HCE variables: {}'.format(kwargs['hce']))
    status_logger.info('- Free text variables: {}'.format(kwargs['freetext']))
    status_logger.info('')

    # Note - does not work on Windows with Python 2.7, does work elsewhere.
    _init_handle_shutdown()

    status_notifier.register(CommandLineNotificationHandler())

    global worker
    worker = workerthread.WorkerThread(kwargs['input'], kwargs['hce'], kwargs['output'],
                                       kwargs['freetext'], kwargs['malaria'], kwargs['country'],
                                       completion_callback=_completion_handler)


def _completion_handler(status, message=''):
    """
    Completion event handler. Prints the result.
    :type status: int
    """
    if status == workerthread.CompletionStatus.ABORT:
        status_logger.info('Computation aborted.')
    elif status == workerthread.CompletionStatus.DONE:
        status_logger.info('Process completed.')
    if message:
        status_logger.info(message)
    sys.exit(status)


def _init_handle_shutdown():
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)


def _shutdown(signum, frame):
    global worker
    try:
        worker.abort()
    except AttributeError:
        pass  # Worker has not been started.


class CommandLineNotificationHandler(object):
    def __init__(self):
        self._progress_bar = None

    def __call__(self, *args, **kwargs):
        self._handle_notification(*args, **kwargs)

    def _update_gauge(self, progress, label=''):
        """
        Update a gauge value and range.
        :param progress: List, set, or tuple with the first pos as the value, and second pos as the range.
        :type progress: (list, set, tuple)
        """
        if progress is None:
            if self._progress_bar:
                self._progress_bar.finish()
        elif isinstance(progress, int):
            self._progress_bar.update(self._progress_bar.currval + progress)
        elif isinstance(progress, (list, set, tuple)):
            if len(progress) > 1:
                if progress[1]:
                    self._progress_bar = ProgressBar(widgets=[label, Bar(), ETA()], maxval=progress[1])
                    self._progress_bar.start()
            else:
                self._progress_bar.update(progress[0])

    def _show_message(self, message_data):
        """
        Display a simple message dialog.
        :param message_data: List, set, or tuple with the first pos as the message, and second pos as the style.
        :type message_data: (list, set, tuple)
        """
        status_logger.info(message_data)

    def _handle_notification(self, data):
        """
        Processes status notification updates into progress bar updates.

        :type data: dict
        :param data: Dictionary of status update metadata.
        """
        if 'sub_progress' in data:
            self._update_gauge(data['sub_progress'], data.get('label', ''))
        if 'message' in data:
            self._show_message(data['message'])


if __name__ == '__main__':
    main()
