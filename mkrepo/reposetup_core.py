# -*- coding: utf-8 -*-

"""Main module."""

import logging
import os
from configparser import ConfigParser
from collections import OrderedDict


from mkrepo import reposync
from mkrepo import utils

LOGGER = logging.getLogger(__name__)


class ReposetupError(Exception):
    pass


class RepomanError(Exception):
    pass


def reposetup(
    dest, sync_dir, sync, yum_config,
    repoman_config, custom_source
):
    try:
        _reposetup(
            dest=dest,
            sync_dir=sync_dir,
            sync=sync,
            yum_config=yum_config,
            repoman_config=repoman_config,
            custom_source=custom_source
        )
        LOGGER.info('Successfully created repo {}'.format(dest))
    except Exception as e:
        LOGGER.error('Failed to create repo {}'.format(dest))
        debug_err(e)
        raise ReposetupError(str(e))


def _reposetup(
    dest, sync_dir, sync,
    yum_config, repoman_config, custom_source
):
    """Run the main flow

    Args:
        dest (str)
        sync_dir (str)
        sync (bool)
        yum_config (str)
        repoman_config (str)
        custom_source (list)
    """
    repoid_to_path = get_repo_paths(sync_dir, yum_config)
    utils.safe_mkdir(dest, *repoid_to_path.values())
    lock_timeout = 180

    with utils.LockFiles(
            [dest] + repoid_to_path.values(),
            timeout=lock_timeout,
            lock_name='mkrepo.lock'
    ):
        if sync:
            do_sync(yum_config, sync_dir, repoid_to_path.keys())

        do_merge(
            custom_source
            + [r + ':only-missing' for r in repoid_to_path.values()],
            dest,
            repoman_config
        )


def get_repo_paths(sync_dir, yum_config):
    if yum_config:
        return _get_repo_paths(sync_dir, yum_config)

    return {}


def _get_repo_paths(sync_dir, yum_config):
    """Get the paths where each repo will be synced

    Args:
        sync_dir (str)
        yum_config (str)

    Returns:
        OrderedDict: repoid to dir
    """
    cp = ConfigParser()
    try:
        with open(yum_config) as f:
            cp.read_file(f)
    except OSError as e:
        LOGGER.error('Failed to read {}'.format(yum_config))
        debug_err(e)
        raise

    return OrderedDict(
        [
            (repoid, os.path.join(sync_dir, repoid))
            for repoid in cp.sections()
            if repoid != 'main'
        ]
    )


def do_sync(yum_config, sync_dir, repoids):
    if yum_config and repoids:
        reposync.sync(yum_config, sync_dir, repoids)
    elif yum_config:
        LOGGER.debug('Yum config is empty')
    else:
        LOGGER.debug('Yum config not provided, skipping sync')


def do_merge(sources, dest, repoman_config=None):
    """
    Run repoman on ``sources``, creating a new RPM repository in
    ``dest``

    Args:
        sources(list of str): repoman sources
        dest(str): Path to create new repository
        repoman_config(str): A path to a repoman configuration file,
            if not passed it will use default repoman configurations,
            equivalent to:

            |  [main]
            |  on_empty_source=warn
            |  [store.RPMStore]
            |  on_wrong_distro=copy_to_all
            |  with_srcrpms=false
            |  with_sources=false

    Raises:
        :exc:`RepositoryMergeError`: If repoman command failed.
        :exc:`IOError`: If ``repoman_config`` is passed but does not exists.

    Returns:
        None
    """
    cmd = []
    cmd_suffix = [
        '--option=store.RPMStore.rpm_dir=', dest, 'add'
    ] + sources
    if repoman_config is None:
        repoman_params = [
            '--option=main.on_empty_source=warn',
            '--option=store.RPMStore.on_wrong_distro=copy_to_all',
            '--option=store.RPMStore.with_srcrpms=false',
            '--option=store.RPMStore.with_sources=false',
        ]
        cmd = ['repoman'] + repoman_params + cmd_suffix
    else:
        if os.path.isfile(repoman_config):
            cmd = ['repoman', '--config={0}'.format(repoman_config)
                   ] + cmd_suffix
        else:
            raise IOError(
                ('error running repoman, {0} not '
                 'found').format(repoman_config)
            )

    LOGGER.info('Running repoman')

    ret, out, err = utils.run_command(cmd)
    if ret:
        raise RepomanError(
            (
                'Failed merging repoman sources: {} into directory: {}\n'
                '{}'
            ).format(sources, dest, err)
        )


def debug_err(err):
    LOGGER.debug(str(err), exc_info=True)
