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

import caniusepython3 as ciu
from caniusepython3.test import unittest, skip_pypi_timeouts

import tempfile

py2_project = 'pulp'  # https://pypi.org/project/PuLP/

EXAMPLE_METADATA = """Metadata-Version: 1.2
Name: TestingMetadata
Version: 0.5
Summary: testing
Home-page: http://github.com/brettcannon/caniusepython3
Author: Brett Cannon
Author-email: brett@python.org
License: Apache
Requires-Dist: {0}
""".format(py2_project)


class CheckTest(unittest.TestCase):

    # When testing input, make sure to use project names that **will** lead to
    # a False answer since unknown projects are skipped.

    @skip_pypi_timeouts
    def test_success(self):
        self.assertTrue(ciu.check(projects=['scipy', 'numpy', 'ipython']))

    @skip_pypi_timeouts
    def test_failure(self):
        self.assertFalse(ciu.check(projects=[py2_project]))

    @skip_pypi_timeouts
    def test_requirements(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(py2_project+'\n')
            file.flush()
            self.assertFalse(ciu.check(requirements_paths=[file.name]))

    @skip_pypi_timeouts
    def test_metadata(self):
        self.assertFalse(ciu.check(metadata=[EXAMPLE_METADATA]))

    @skip_pypi_timeouts
    def test_projects(self):
        # Implicitly done by test_success and test_failure.
        pass

    @skip_pypi_timeouts
    def test_case_insensitivity(self):
        funky_name = (py2_project[:len(py2_project)].lower() +
                      py2_project[len(py2_project):].upper())
        self.assertFalse(ciu.check(projects=[funky_name]))

    @skip_pypi_timeouts
    def test_ignore_missing_projects(self):
        self.assertTrue(ciu.check(projects=['sdfsjdfsdlfk;jasdflkjasdfdfsdf']))

    @skip_pypi_timeouts
    def test_manual_overrides(self):
        self.assertTrue(ciu.check(projects=["unittest2"]))
