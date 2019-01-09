#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `mkrepo` package."""

import pytest
import tempfile
from collections import OrderedDict

from click.testing import CliRunner

from mkrepo.reposetup_core import (
    get_repo_paths
)

from mkrepo import cli


@pytest.fixture
def tmpfile():
    with tempfile.NamedTemporaryFile(mode='r+t') as f:
        yield f.name


@pytest.mark.parametrize(
    'sync_dir,config_str,expected', [
    (
        '/var/cache/mkrepo',
        '[main]\n[repo_a]\n[repo_b]\n',
        OrderedDict([
            ('repo_a', '/var/cache/mkrepo/repo_a'), 
            ('repo_b', '/var/cache/mkrepo/repo_b'),
        ])
    ),
    ]
)
def test_get_repo_paths_should_sucess(sync_dir, config_str, expected, tmpfile):
    with open(tmpfile, mode='r+t') as f:
        f.write(config_str)

    result = get_repo_paths(sync_dir, tmpfile)
    assert result == expected


def test_get_repo_paths_shoud_fail_if_config_does_not_exist():
    with pytest.raises(IOError):
        get_repo_paths('/var/cache/mkrepo', 'not_exists')
