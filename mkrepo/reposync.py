"""Wrapper around reposync"""

import logging
import re
import itertools
import os
import tempfile
import shutil

from mkrepo import utils

LOGGER = logging.getLogger(__name__)


class ReposyncError(Exception):
    pass


def sync(yum_config, sync_dir, repoids):
    utils.safe_mkdir(sync_dir)
    cache_dir = tempfile.mkdtemp(prefix='reposync_')
    LOGGER.debug('Using {} as cache dir for reposync'.format(
        cache_dir
    ))
    base_cmd = [
        'reposync', '--config', yum_config,
        '--newest-only', '--delete',
        '--cachedir', cache_dir,
        '--download_path', sync_dir,
    ]

    LOGGER.info('Running reposync')
    try:
        for repoid in repoids:
            LOGGER.info('Syncing {}'.format(repoid))
            cmd = base_cmd + ['--repoid', repoid]

            ret, out, _ = utils.run_command(cmd)
            if not ret:
                LOGGER.info('Successfully synced {}'.format(repoid))
                continue

            LOGGER.info('Failed to sync {}, re-running'.format(repoid))
            _fix_reposync_issues(
                out,
                os.path.join(sync_dir, repoid),
            )
            ret = utils.run_command(cmd)
            if not ret:
                continue

            LOGGER.info(
                'Failed to sync {} '
                'clearing cache and re-running'.format(repoid)
            )
            shutil.rmtree(cache_dir)
            os.mkdir(cache_dir)
            ret, out, err = utils.run_command(cmd)

            if ret:
                LOGGER.error(
                    'Reposync command failed for {}\n'
                    'stdout:\n\t{}\n'
                    'stderr:\n\t{}\n'.format(repoid, out, err)
                )
            raise ReposyncError('Failed to run Reposync')
    finally:
        shutil.rmtree(cache_dir)


def _fix_reposync_issues(reposync_out, repo_path):
    """
    Fix for the issue described at::
        https://bugzilla.redhat.com//show_bug.cgi?id=1399235
        https://bugzilla.redhat.com//show_bug.cgi?id=1332441

    """
    if len(repo_path) == 0 or len(reposync_out) == 0:
        LOGGER.warning(
            (
                'unable to run _fix_reposync_issues, no reposync output '
                'or empty repo path.'
            )
        )
        return
    rpm_regex = r'[a-z]{1}[a-zA-Z0-9._\\-]+'
    wrong_version = re.compile(
        r'(?P<package_name>' + rpm_regex + r'): \[Errno 256\]'
    )
    wrong_release = re.compile(r'(?P<package_name>' + rpm_regex + r') FAILED')
    packages = set(
        itertools.chain(
            wrong_version.findall(reposync_out),
            wrong_release.findall(reposync_out)
        )
    )
    count = 0
    LOGGER.debug(
        'detected package errors in reposync output in repo_path:%s: %s',
        repo_path, ','.join(packages)
    )

    for dirpath, _, filenames in os.walk(repo_path):
        rpms = (
            file for file in filenames
            if file.endswith('.rpm') and dirpath.startswith(repo_path)
        )
        for rpm in rpms:
            if any(map(rpm.startswith, packages)):
                bad_package = os.path.join(dirpath, rpm)
                LOGGER.info('removing conflicting RPM: %s', bad_package)
                os.unlink(bad_package)
                count = count + 1

    if count > 0:
        LOGGER.debug(
            (
                'removed %s conflicting packages, see '
                'https://bugzilla.redhat.com//show_bug.cgi?id=1399235 '
                'for more details.'
            ), count
        )
