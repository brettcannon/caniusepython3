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

from __future__ import unicode_literals

import distlib.locators

import concurrent.futures
import json
import logging
import multiprocessing
import pkgutil
import re
import sys
try:
    import urllib.request as urllib_request
except ImportError:
    import urllib2 as urllib_request
import xml.parsers.expat
try:
    import xmlrpc.client as xmlrpc_client
except ImportError:
    import xmlrpclib as xmlrpc_client

try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:
    CPU_COUNT = 2

PROJECT_NAME = re.compile(r'[\w.-]+')

# Without this, the 'ciu' logger will emit nothing.
logging.basicConfig(format='[%(levelname)s] %(msg)s')


class LowerDict(dict):

    def __getitem__(self, key):
        return super(LowerDict, self).__getitem__(key.lower())

    def __setitem__(self, key, value):
        return super(LowerDict, self).__setitem__(key.lower(), value)


def overrides():
    """Load a set containing projects who are missing the proper Python 3 classifier.

    Project names are always lowercased.

    """
    raw_bytes = pkgutil.get_data(__name__, 'overrides.json')
    return frozenset(json.loads(raw_bytes.decode('utf-8')).keys())


def py3_classifiers():
    """Fetch the Python 3-related trove classifiers."""
    url = 'https://pypi.python.org/pypi?%3Aaction=list_classifiers'
    response = urllib_request.urlopen(url)
    try:
        try:
            status = response.status
        except AttributeError:
            status = response.code
        if status != 200:
            msg = 'PyPI responded with status {0} for {1}'.format(status, url)
            raise ValueError(msg)
        data = response.read()
    finally:
        response.close()
    classifiers = data.decode('utf-8').splitlines()
    base_classifier = 'Programming Language :: Python :: 3'
    return (classifier for classifier in classifiers
            if classifier.startswith(base_classifier))


def projects_matching_classifier(classifier):
    """Find all projects matching the specified trove classifier."""
    log = logging.getLogger('ciu')
    client = xmlrpc_client.ServerProxy('http://pypi.python.org/pypi')
    try:
        log.info('Fetching project list for {0!r}'.format(classifier))
        return frozenset(result[0].lower()
                         for result in client.browse([classifier]))
    except xml.parsers.expat.ExpatError:
        # Python 2.6 doesn't like empty results.
        log.info("PyPI didn't return any results")
        return frozenset()
    finally:
        try:
            client('close')()
        except xml.parsers.expat.ExpatError:
            # The close hack is not in Python 2.6.
            pass


def all_py3_projects(manual_overrides=None):
    log = logging.getLogger('ciu')
    projects = set()
    thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=CPU_COUNT)
    with thread_pool_executor as executor:
        for result in map(projects_matching_classifier, py3_classifiers()):
            projects.update(result)
    if manual_overrides is None:
        manual_overrides = overrides()
    stale_overrides = projects.intersection(manual_overrides)
    log.info('Adding {0} overrides'.format(len(manual_overrides)))
    if stale_overrides:
        log.warn('Stale overrides: {0}'.format(stale_overrides))
    projects.update(manual_overrides)
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
    log = logging.getLogger('ciu')
    deps = []
    log.info('Locating {0}'.format(project_name))
    located = distlib.locators.locate(project_name, prereleases=True)
    if located is None:
        log.warn('{0} not found'.format(project_name))
        return None
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
    reasons = LowerDict((project, None) for project in check)
    thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=CPU_COUNT)
    with thread_pool_executor as executor:
        while len(check) > 0:
            new_check = []
            for parent, deps in zip(check, executor.map(dependencies, check)):
                if deps is None:
                    # Can't find any results for a project, so ignore it so as
                    # to not accidentally consider indefinitely that a project
                    # can't port.
                    del reasons[parent]
                    continue
                for dep in deps:
                    if dep in py3_projects:
                        continue
                    reasons[dep] = parent
                    new_check.append(dep)
            check = new_check
    return reasons_to_paths(reasons)
