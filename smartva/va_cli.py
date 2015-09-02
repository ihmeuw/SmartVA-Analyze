import click

from smartva import prog_name, version
from smartva import workerthread

worker = None


@click.command()
@click.option('--country', default='UNKNOWN', help='Data origin country.')
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

    global worker
    worker = workerthread.WorkerThread(kwargs['input'], kwargs['hce'], kwargs['output'],
                                       kwargs['freetext'], kwargs['malaria'], kwargs['country'],
                                       completion_callback=completion)


def completion(event):
    print(event)


if __name__ == '__main__':
    main()
