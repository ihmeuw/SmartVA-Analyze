import signal
import click
import sys

from smartva import prog_name, version
from smartva import workerthread
from smartva.countries import COUNTRIES, COUNTRY_DEFAULT

worker = None


def check_country(ctx, param, value):
    """
    Check that the specified country is in the list of valid countries. If not, print out a list of valid countries.
    """
    if not value.upper() in (country.split(' ')[-1].strip('()').upper() for country in COUNTRIES):
        click.echo('Country list:')
        for country in COUNTRIES:
            click.echo(u'- {}'.format(country))
        ctx.exit()
    return value.upper()


@click.command()
@click.option('--country', default=COUNTRY_DEFAULT, callback=check_country,
              help='Data origin country (abbreviation). "LIST" to display all.')
@click.option('--malaria', default=True, type=click.BOOL, help='Data is a from Malaria region.')
@click.option('--hce', default=True, type=click.BOOL, help='Use Health Care Experience (HCE) variables.')
@click.option('--freetext', default=True, type=click.BOOL, help='Use "free text" variables.')
@click.version_option(version=version, prog_name=prog_name)
@click.argument('input', type=click.Path(file_okay=True, dir_okay=False, readable=True, exists=True))
@click.argument('output', type=click.Path(file_okay=False, dir_okay=True, writable=True, exists=True))
# @click.option('--config', help='Specify options in a YAML file.')
# @click.option('--about', help='About this application.)
def main(*args, **kwargs):
    click.echo('country {}'.format(kwargs['country']))
    click.echo('malaria {}'.format(kwargs['malaria']))
    click.echo('hce {}'.format(kwargs['hce']))
    click.echo('freetext {}'.format(kwargs['freetext']))
    click.echo('input {}'.format(kwargs['input']))
    click.echo('output {}'.format(kwargs['output']))

    # Note - does not work on Windows with Python 2.7, does work elsewhere.
    _init_handle_shutdown()

    global worker
    worker = workerthread.WorkerThread(kwargs['input'], kwargs['hce'], kwargs['output'],
                                       kwargs['freetext'], kwargs['malaria'], kwargs['country'],
                                       completion_callback=completion)


def completion(event):
    """
    Completion event handler. Prints the result.
    :type event: int
    """
    if event == workerthread.CompletionStatus.ABORT:
        click.echo('Computation successfully aborted')
    elif event == workerthread.CompletionStatus.DONE:
        click.echo('Process complete')
    sys.exit(event)


def _init_handle_shutdown():
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)


def _shutdown(signum, frame):
    global worker
    worker.abort()
