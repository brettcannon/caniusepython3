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

from caniusepython3 import pypi
from caniusepython3.test import unittest, skip_pypi_timeouts

import packaging.utils


class NameTests(unittest.TestCase):

    def test_simple(self):
        want = 'simple-name_with.everything-separator_known'
        got = pypi.just_name(want)
        self.assertEqual(got, want)

    def test_requirements(self):
        want = 'project.name'
        got = pypi.just_name(want + '>=2.0.1')
        self.assertEqual(got, want)

    def test_bad_requirements(self):
        # From the OpenStack requirements file:
        # https://raw2.github.com/openstack/requirements/master/global-requirements.txt
        want = 'warlock'
        got = pypi.just_name(want + '>1.01<2')
        self.assertEqual(got, want)

    def test_metadata(self):
        want = 'foo'
        got = pypi.just_name("foo; sys.platform == 'okook'")
        self.assertEqual(got, want)


class OverridesTests(unittest.TestCase):

    @skip_pypi_timeouts
    def test_canonicalization(self):
        for name in pypi.manual_overrides():
            self.assertEqual(name, packaging.utils.canonicalize_name(name))

    @skip_pypi_timeouts
    def test_success(self):
        overrides = pypi.manual_overrides()
        self.assertTrue(len(overrides) > 10)
        self.assertIn("unittest2", overrides)


class NetworkTests(unittest.TestCase):

    @skip_pypi_timeouts
    def test_supports_py3(self):
        self.assertTrue(pypi.supports_py3("caniusepython3"))
        self.assertFalse(pypi.supports_py3("pil"))
        # Unfound projects are considered ported.
        self.assertTrue(pypi.supports_py3("sdfffavsafasvvavfdvavfavf"))
