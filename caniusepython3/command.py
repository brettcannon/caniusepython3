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

import setuptools
import sys

import caniusepython3 as ciu
import caniusepython3.__main__ as ciu_main
from caniusepython3 import pypi


class Command(setuptools.Command):

    description = """Run caniusepython3 over a setup.py file."""

    user_options = []

    def _dependencies(self):
        projects = []
        for attr in ('install_requires', 'tests_require'):
            requirements = getattr(self.distribution, attr, None) or []
            for project in requirements:
                if not project:
                    continue
                projects.append(pypi.just_name(project))
        extras = getattr(self.distribution, 'extras_require', None) or {}
        for value in extras.values():
            projects.extend(map(pypi.just_name, value))
        return projects

    def initialize_options(self):
        pass

    def run(self):
        passed = ciu_main.check(self._dependencies())
        if not passed:
            sys.exit(3)

    def finalize_options(self):
        pass
