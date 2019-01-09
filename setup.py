#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from os import path, curdir
import re
from setuptools import setup, find_packages
from subprocess import check_output


def get_version():
    return get_version_from_pkg_metadata() or get_version_from_git()


def get_version_from_pkg_metadata(project_dir=curdir):
    pkg_info_file = path.join(project_dir, 'PKG-INFO')
    try:
        with open(pkg_info_file) as f:
            for line in f.readlines():
                if line.startswith('Version: '):
                    return line.split(' ', 1)[-1].strip()
    except IOError:
        pass

    return None


def get_version_from_git():
    p = re.compile(r'(?P<major>[0-9]+)\.(?P<minor>[0-9]+)-(?P<patch>[0-9]+)-(?P<sha>[a-z0-9]+)')
    git_desc = check_output(['git', 'describe', '--tags', '--long'])
    m = p.match(git_desc)
    if not m:
        raise RuntimeError('Failed to parse git output: {}'.format(git_desc))

    return '{major}.{minor}.{patch}+{sha}'.format(**m.groupdict())


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as f:
    requirements = f.read()


setup(
    author="Gal Ben Haim",
    author_email='galbh2@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    description="Build Yum/DNF repositories from multiple sources",
    entry_points={
        'console_scripts': [
            'mkrepo=mkrepo.cli:cli',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='mkrepo',
    name='mkrepo',
    packages=find_packages(include=['mkrepo']),
    url='https://github.com/gbenhaim/mkrepo',
    version=get_version(),
    zip_safe=False,
)
