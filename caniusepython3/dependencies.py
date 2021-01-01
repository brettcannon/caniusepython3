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

from __future__ import unicode_literals

import setuptools  # To silence a warning.
import distlib.locators
import packaging.utils

import caniusepython3 as ciu
from caniusepython3 import pypi

import concurrent.futures
import logging


class CircularDependencyError(Exception):
    """Raised if there are circular dependencies detected."""


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
            if parent in path:
                raise CircularDependencyError(dict(parent=parent,
                                                   blocker=blocker,
                                                   path=path))
            path.append(parent)
            parent = reasons.get(parent)
        paths.add(tuple(path))
    return paths


def dependencies(project_name):
    """Get the dependencies for a project."""
    log = logging.getLogger('ciu')
    log.info('Locating dependencies for {}'.format(project_name))
    located = distlib.locators.locate(project_name, prereleases=True)
    if not located:
        log.warning('{0} not found; false-negatives possible'.format(project_name))
        return None
    return {packaging.utils.canonicalize_name(pypi.just_name(dep))
            for dep in located.run_requires}


def blockers(project_names, index_url=pypi.PYPI_INDEX_URL):
    log = logging.getLogger('ciu')
    overrides = pypi.manual_overrides()

    def supports_py3(project_name):
        if project_name in overrides:
            return True
        else:
            return pypi.supports_py3(project_name, index_url=index_url)

    check = []
    evaluated = set(overrides)
    for project in project_names:
        log.info('Checking top-level project: {0} ...'.format(project))
        evaluated.add(project)
        if not supports_py3(project):
            check.append(project)
    reasons = {project: None for project in check}
    thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=ciu.CPU_COUNT)
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
                log.info('Dependencies of {0}: {1}'.format(project, deps))
                unchecked_deps = []
                for dep in deps:
                    if dep in evaluated:
                        log.info('{0} already checked'.format(dep))
                    else:
                        unchecked_deps.append(dep)
                deps_status = zip(unchecked_deps,
                                  executor.map(supports_py3,
                                               unchecked_deps))
                for dep, ported in deps_status:
                    if not ported:
                        reasons[dep] = parent
                        new_check.append(dep)
                    # Make sure there's no data race in recording a dependency
                    # has been evaluated but not reported somewhere.
                    evaluated.add(dep)
            check = new_check
    return reasons_to_paths(reasons)
