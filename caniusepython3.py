#! /usr/bin/env python3

# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Calculate whether the specified and their dependencies support Python 3."""

import distlib.locators
import distlib.metadata
import pkg_resources

import argparse
import io
import logging
import re
import sys
import xmlrpc.client

NEWEST_MINOR_VERSION = 4
if sys.version_info.major == 3:
    assert NEWEST_MINOR_VERSION >= sys.version_info.minor

PROJECT_NAME = re.compile(r'[\w.-]+')

OVERRIDES = {x.lower() for x in {
    'beautifulsoup',  # beautifulsoup4
    'ipaddress',  # stdlib
    'mox',  # mox3
    'mox3', # Missing classifier
    'multiprocessing',  # stdlib
    'ordereddict', # stdlib
    'pbr',  # Missing classifier
    'pylint',  # Missing classifier
    'pyopenssl',  # Missing classifier
    'pysqlite',  # stdlib
    'python-keystoneclient',  # Missing classifier
    'python-memcached',  # python3-memcached
    'python-novaclient',  # Missing classifier
    'pyvirtualdisplay',  # Missing classifier
    'rsa',  # Missing classifier
    'ssl',  # stdlib
    'trollius',  # asyncio
    'unittest2',  # stdlib
    'uuid',  # stdlib
    'wsgiref',  #stdlib
    'xlwt',  # xlwt-future
    'zc.recipe.egg',  # Missing classifier
}}


class LowerDict(dict):

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)


def all_py3_projects():
    base_classifier = 'Programming Language :: Python :: 3'
    classifiers = [base_classifier]
    classifiers.extend('{}.{}'.format(base_classifier, i)
                       for i in range(NEWEST_MINOR_VERSION + 1))
    projects = set()
    client = xmlrpc.client.ServerProxy('http://pypi.python.org/pypi')
    try:
        for classifier in classifiers:
            logging.info('Fetching project list for {!r}'.format(classifier))
            projects.update(result[0].lower()
                            for result in client.browse([classifier]))
    finally:
        client('close')()
    stale_overrides = projects.intersection(OVERRIDES)
    logging.info('Adding {} overrides'.format(len(OVERRIDES)))
    if stale_overrides:
        logging.warn('Stale overrides: {}'.format(stale_overrides))
    projects.update(OVERRIDES)
    return projects


def just_name(supposed_name):
    return PROJECT_NAME.match(supposed_name).group(0).lower()


def reasons_to_paths(reasons):
    """Calculate the dependency paths to the reasons of the blockers.

    Paths will be in reverse-dependency order (i.e. parent projects are in
    ascending order).

    """
    blockers = set(reasons.keys()) - set(reasons.values())
    paths = set()
    for blocker in blockers:
        path = [blocker]
        parent = reasons[blocker]
        while parent:
            path.append(parent)
            parent = reasons.get(parent)
        paths.add(tuple(path))
    return paths


def blocking_dependencies(projects, py3_projects):
    """Starting from 'projects', find all projects which are blocking Python 3 usage.

    Any project in 'py3_projects' is considered ported and thus will not have
    its dependencies searched. Version requirements are also ignored as it is
    assumed that if a project is updating to support Python 3 then they will be
    willing to update to the latest version of their dependencies. The only
    dependencies checked are those required to run the project.

    """
    check = [project.lower()
             for project in projects if project.lower() not in py3_projects]
    reasons = LowerDict({project: None for project in check})
    while len(check) > 0:
        project = check.pop(0)
        logging.info('Locating {}'.format(project))
        located = distlib.locators.locate(project, prereleases=True)
        if located is None:
            logging.warn('{} not found'.format(project))
            continue
        for dep in located.run_requires:
            # Drop any version details from the dependency name.
            dep_name = just_name(dep)
            if dep_name in py3_projects:
                continue
            reasons[dep_name] = project
            check.append(dep_name)
    return reasons_to_paths(reasons)


def projects_from_requirements(requirements):
    """Extract the project dependencies from a Requirements specification."""
    reqs = pkg_resources.parse_requirements(requirements)
    return [req.project_name for req in reqs]


def projects_from_metadata(metadata):
    """Extract the project dependencies from a metadata spec."""
    meta = distlib.metadata.Metadata(fileobj=io.StringIO(metadata))
    return [just_name(project) for project in meta.run_requires]


def projects_from_cli(args):
    """Take arguments through the CLI can create a list of specified projects."""
    description = ('Determine if a set of project dependencies will work with '
                   'Python 3')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--requirements', nargs='?',
        help='path to a pkg_resources requirements file (e.g. requirements.txt)')
    parser.add_argument('--metadata', nargs='?',
        help='path to a PEP 426 metadata file (e.g. PKG-INFO, pydist.json)')
    parser.add_argument('--projects', type=lambda arg: arg.split(','), nargs='?',
        help='a comma-separated list of projects')
    parser.add_argument('--verbose', action='store_true', help='verbose output')
    parsed = parser.parse_args(args)

    projects = []
    if parsed.verbose:
        logging.getLogger().setLevel(logging.INFO)
    if parsed.requirements:
        with open(parsed.requirements) as file:
            projects.extend(projects_from_requirements(file.read()))
    if parsed.metadata:
        with open(parsed.metadata) as file:
            projects.extend(projects_from_metadata(file.read()))
    if parsed.projects:
        projects.extend(parsed.projects)

    return projects


if __name__ == '__main__':
    projects = projects_from_cli(sys.argv[1:])
    logging.info('{} top-level projects to check'.format(len(projects)))
    print('Finding and checking dependencies ...')
    blocking = blocking_dependencies(projects, all_py3_projects())
    flattened_blockers = set()
    for blocker_reasons in blocking:
        for blocker in blocker_reasons:
            flattened_blockers.add(blocker)
    print()
    print('{} total dependencies need to be ported to Python 3.'.format(len(flattened_blockers)))
    print('{} dependencies have no other dependencies blocking a port to Python 3:'.format(len(blocking)))
    for blocker in sorted(blocking, key=lambda x: tuple(reversed(x))):
        print(' <- '.join(blocker))
