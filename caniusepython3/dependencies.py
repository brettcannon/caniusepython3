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
    deps = []
    log.info('Locating {0}'.format(project_name))
    located = distlib.locators.locate(project_name, prereleases=True)
    if not located:
        log.warning('{0} not found'.format(project_name))
        return None
    for dep in map(packaging.utils.canonicalize_name, located.run_requires):
        # Drop any version details from the dependency name.
        deps.append(pypi.just_name(dep))
    return deps


def blocking_dependencies(projects, py3_projects):
    """Starting from 'projects', find all projects which are blocking Python 3 usage.

    Any project in 'py3_projects' is considered ported and thus will not have
    its dependencies searched. Version requirements are also ignored as it is
    assumed that if a project is updating to support Python 3 then they will be
    willing to update to the latest version of their dependencies. The only
    dependencies checked are those required to run the project.

    """
    log = logging.getLogger('ciu')
    check = []
    evaluated = set()
    for project in map(packaging.utils.canonicalize_name, projects):
        log.info('Checking top-level project: {0} ...'.format(project))
        try:
            dist = distlib.locators.locate(project)
        except AttributeError:
            # This is a work around. //bitbucket.org/pypa/distlib/issue/59/ .
            log.warning('{0} found but had to be skipped.'.format(project))
            continue
        if not dist:
            log.warning('{0} not found'.format(project))
            continue
        project = dist.name.lower()  # PyPI can be forgiving about name formats.
        if project not in py3_projects:
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
                for dep in deps:
                    log.info('Checking dependency: {0} ...'.format(dep))
                    if dep in evaluated:
                        log.info('{0} already checked'.format(dep))
                        continue
                    else:
                        evaluated.add(dep)
                    if dep in py3_projects:
                        continue
                    reasons[dep] = parent
                    new_check.append(dep)
            check = new_check
    return reasons_to_paths(reasons)
