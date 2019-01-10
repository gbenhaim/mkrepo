# -*- coding: utf-8 -*-

"""Console script for ir."""
from __future__ import print_function

import click
from pkg_resources import get_distribution
import logging
from textwrap import dedent

from mkrepo import reposetup_core


LOGGER = logging.getLogger(__name__)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--log-level', '-l',
    type=click.Choice(['info', 'debug']),
    default='info',
    show_default=True,
    help='Log level to use'
)
def cli(log_level):
    setup_logging(level=log_level)


@cli.command()
@click.option(
    '--custom-source',
    type=click.Path(exists=True, resolve_path=True, readable=True),
    metavar='<custom-source>',
    multiple=True,
    help=dedent(
        """
        Add an extra RPM source to the target repo.
        RPMs are added to the target repo by the order they apper
        in the custom-source list, and before any RPM from the
        RPM cache is being added. It means the different order,
        will can result in a different target repo.
        Allow any source string allowed by repoman.
        """
    )
)
@click.option(
    '--repoman-config',
    type=click.Path(resolve_path=True, file_okay=True),
    metavar='<repoman-config>',
    help='A config for repoman. '
         'Note that store.RPMStore.rpm_dir is not configurable.',
)
@click.option(
    '--yum-config',
    type=click.Path(exists=True, resolve_path=True, readable=True),
    metavar='<yum-config>',
    help=dedent(
        """
        Yum config to use for syncing the RPM cache,
        and building the target repo.
        If not specified, cache sync will be skipped.
        """
    )
)
@click.option(
    '--sync/--skip-sync',
    default=True,
    show_default=True,
    metavar='<sync>',
    help='Sync RPM cache or not',
)
@click.option(
    '--sync-dir',
    type=click.Path(dir_okay=True, resolve_path=True),
    default='/var/cache/mkrepo',
    show_default=True,
    metavar='<sync-dir>',
    help='Where to store RPM cache'
)
@click.option(
    '--dest',
    type=click.Path(dir_okay=True, resolve_path=True),
    required=True,
    metavar='<dest>',
    help='Where to create the repo',
)
def reposetup(dest, sync_dir, sync, yum_config, repoman_config, custom_source):
    """Run the main flow"""
    try:
        reposetup_core.reposetup(
            dest=dest,
            sync_dir=sync_dir,
            sync=sync,
            yum_config=yum_config,
            repoman_config=repoman_config,
            custom_source=list(custom_source)
        )
    except reposetup_core.ReposetupError as e:
        LOGGER.error('Failed to run reposetup: {}'.format(str(e)))


@cli.command()
def version():
    """Print version and exit"""
    print(get_distribution('mkrepo').version)


def setup_logging(level):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
    )
