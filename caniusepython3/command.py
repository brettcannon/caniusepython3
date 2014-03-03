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

import setuptools

import caniusepython3 as ciu
import caniusepython3.__main__ as ciu_main


class Command(setuptools.Command):

    description = """Run caniusepython3 over a setup.py file."""

    user_options = []

    _require_fields = ('install_requires', 'extras_require', 'setup_requires',
                       'tests_require')

    def initialize_options(self):
        pass

    def run(self):
        projects = []
        for attr in self._require_fields:
            requirements = getattr(self.distribution, attr, None) or []
            for project in requirements:
                if not project:
                    continue
                projects.append(ciu.just_name(project))
        ciu_main.check(projects)

    def finalize_options(self):
        pass
