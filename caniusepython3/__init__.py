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

from caniusepython3 import projects as projects_
from caniusepython3 import pypi

import multiprocessing


try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:  #pragma: no cover
    CPU_COUNT = 2


def check(requirements_paths=[], metadata=[], projects=[]):
    """Return True if all of the specified dependencies have been ported to Python 3.

    The requirements_paths argument takes a sequence of file paths to
    requirements files. The 'metadata' argument takes a sequence of strings
    representing metadata. The 'projects' argument takes a sequence of project
    names.

    Any project that is not listed on PyPI will be considered ported.
    """
    dependencies = []
    dependencies.extend(projects_.projects_from_requirements(requirements_paths))
    dependencies.extend(projects_.projects_from_metadata(metadata))
    dependencies.extend(projects)

    manual_overrides = pypi.manual_overrides()

    for dependency in dependencies:
        if dependency in manual_overrides:
            continue
        elif not pypi.supports_py3(dependency):
            return False
    return True
