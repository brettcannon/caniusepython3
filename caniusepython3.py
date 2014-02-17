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

"""Calculate whether the specified package(s) and their dependencies support Python 3."""

import distlib.locators
import distlib.metadata
import pip.req

import argparse  # Python 3.2
import concurrent.futures  # Python 3.2
import io
import logging
import multiprocessing
import re
import sys
import xmlrpc.client

try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:
    CPU_COUNT = 2

# Make sure we are using all possible trove classifiers to tell if a project
# supports Python 3.
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


def projects_matching_classifier(classifier):
    """Find all projects matching the specified trove classifier."""
    client = xmlrpc.client.ServerProxy('http://pypi.python.org/pypi')
    try:
        logging.info('Fetching project list for {!r}'.format(classifier))
        return (result[0].lower() for result in client.browse([classifier]))
    finally:
        client('close')()


def all_py3_projects():
    base_classifier = 'Programming Language :: Python :: 3'
    classifiers = [base_classifier]
    classifiers.extend('{}.{}'.format(base_classifier, i)
                       for i in range(NEWEST_MINOR_VERSION + 1))
    projects = set()
    thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=CPU_COUNT)
    with thread_pool_executor as executor:
        for result in executor.map(projects_matching_classifier, classifiers):
            projects.update(result)
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


def dependencies(project_name):
    """Get the dependencies for a project."""
    deps = []
    logging.info('Locating {}'.format(project_name))
    located = distlib.locators.locate(project_name, prereleases=True)
    if located is None:
        logging.warn('{} not found'.format(project_name))
        return []
    for dep in located.run_requires:
        # Drop any version details from the dependency name.
        deps.append(just_name(dep))
    return deps


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
    thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=CPU_COUNT)
    with thread_pool_executor as executor:
        while len(check) > 0:
            new_check = []
            for parent, deps in zip(check, executor.map(dependencies, check)):
                for dep in deps:
                    if dep in py3_projects:
                        continue
                    reasons[dep] = parent
                    new_check.append(dep)
            check = new_check
    return reasons_to_paths(reasons)


def projects_from_requirements(requirements_path):
    """Extract the project dependencies from a Requirements specification."""
    reqs = pip.req.parse_requirements(requirements_path)
    return [req.name for req in reqs]


def projects_from_metadata(metadata):
    """Extract the project dependencies from a metadata spec."""
    meta = distlib.metadata.Metadata(fileobj=io.StringIO(metadata))
    return [just_name(project) for project in meta.run_requires]


def projects_from_cli(args):
    """Take arguments through the CLI can create a list of specified projects."""
    description = ('Determine if a set of project dependencies will work with '
                   'Python 3')
    parser = argparse.ArgumentParser(description=description)
    req_help = ('path to a pkg_resources requirements file '
                '(e.g. requirements.txt)')
    parser.add_argument('--requirements', '-r', nargs='?',
                        help=req_help)
    meta_help = 'path to a PEP 426 metadata file (e.g. PKG-INFO, pydist.json)'
    parser.add_argument('--metadata', '-m', nargs='?',
                        help=meta_help)
    parser.add_argument('--projects', '-p', type=lambda arg: arg.split(','),
                        nargs='?', help='a comma-separated list of projects')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='verbose output')
    parsed = parser.parse_args(args)

    projects = []
    if parsed.verbose:
        logging.getLogger().setLevel(logging.INFO)
    if parsed.requirements:
        projects.extend(projects_from_requirements(parsed.requirements))
    if parsed.metadata:
        with open(parsed.metadata) as file:
            projects.extend(projects_from_metadata(file.read()))
    if parsed.projects:
        projects.extend(parsed.projects)

    return projects


def message(blockers):
    """Create a sequence of key messages based on what is blocking."""
    if not blockers:
        return ['You have 0 projects blocking you from using Python 3!']
    flattened_blockers = set()
    for blocker_reasons in blockers:
        for blocker in blocker_reasons:
            flattened_blockers.add(blocker)
    need = 'You need {} project{} to transition to Python 3.'
    formatted_need = need.format(len(flattened_blockers),
                      's' if len(flattened_blockers) != 1 else '')
    can_port = ('Of {} {} project{}, {} {} no direct dependencies blocking '
                '{} transition:')
    formatted_can_port = can_port.format(
            'those' if len(flattened_blockers) != 1 else 'that',
            len(flattened_blockers),
            's' if len(flattened_blockers) != 1 else '',
            len(blockers),
            'have' if len(blockers) != 1 else 'has',
            'their' if len(blockers) != 1 else 'its')
    return formatted_need, formatted_can_port

def pprint_blockers(blockers):
    """Pretty print blockers into a sequence of strings.

    Results will be sorted by top-level project name. This means that if a
    project is blocking another project then the dependent project will be
    what is used in the sorting, not the project at the bottom of the
    dependency graph.

    """
    pprinted = []
    for blocker in sorted(blockers, key=lambda x: tuple(reversed(x))):
        buf = [blocker[0]]
        if len(blocker) > 1:
            buf.append(' (which is blocking ')
            buf.append(', which is blocking '.join(blocker[1:]))
            buf.append(')')
        pprinted.append(''.join(buf))
    return pprinted


def main(args=sys.argv[1:]):
    projects = projects_from_cli(args)
    logging.info('{} top-level projects to check'.format(len(projects)))
    print('Finding and checking dependencies ...')
    blockers = blocking_dependencies(projects, all_py3_projects())

    print()
    for line in message(blockers):
        print(line)

    print()
    for line in pprint_blockers(blockers):
        print(' ', line)


if __name__ == '__main__':
    main()
