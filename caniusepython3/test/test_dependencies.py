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

from caniusepython3 import dependencies, pypi
from caniusepython3.test import mock, unittest

import io


class GraphResolutionTests(unittest.TestCase):

    def test_circular_dependencies(self):
        reasons = {
            'A': 'C',
            'B': 'C',
            'C': 'A',
        }
        self.assertRaises(dependencies.CircularDependencyError,
                          dependencies.reasons_to_paths,
                          reasons)

    def test_all_projects_okay(self):
        # A, B, and C are fine on their own.
        self.assertEqual(set(), dependencies.reasons_to_paths({}))

    def test_leaf_okay(self):
        # A -> B where B is okay.
        reasons = {'A': None}
        self.assertEqual(frozenset([('A',)]),
                         dependencies.reasons_to_paths(reasons))

    def test_leaf_bad(self):
        # A -> B -> C where all projects are bad.
        reasons = {'A': None, 'B': 'A', 'C': 'B'}
        self.assertEqual(frozenset([('C', 'B', 'A')]),
                         dependencies.reasons_to_paths(reasons))


class DependenciesTests(unittest.TestCase):

    @mock.patch('distlib.locators.locate')
    def test_normalization(self, locate_mock):
        class FakeLocated(object):
            def __init__(self, run_requires):
                self.run_requires = run_requires
        fake_deps = FakeLocated(['easy_thumbnail', 'stuff>=4.0.0'])
        locate_mock.side_effect = lambda *args, **kargs: fake_deps
        got = dependencies.dependencies('does not matter')
        self.assertEqual({'easy-thumbnail', 'stuff'}, frozenset(got))

# XXX Tests covering dependency loops, e.g. a -> b, b -> a.

class NetworkTests(unittest.TestCase):

    def test_blockers(self):
        got = frozenset(dependencies.blockers(['ralph_scrooge']))
        if not got:
            self.skipTest("reaching distlib failed")
        else:
            want = frozenset([('ralph', 'ralph_scrooge'), ('ralph-assets', 'ralph_scrooge')])
            self.assertEqual(got, want)

    def test_dependencies(self):
        got = dependencies.dependencies('pastescript')
        if got is None:
            self.skipTest("reaching distlib failed")
        else:
            self.assertEqual(set(got), frozenset(['six', 'pastedeploy', 'paste']))

    def test_dependencies_no_project(self):
        got = dependencies.dependencies('sdflksjdfsadfsadfad')
        self.assertIsNone(got)

    def test_blockers_no_project(self):
        got = dependencies.blockers(['asdfsadfdsfsdffdfadf'])
        self.assertEqual(got, frozenset())

    def test_manual_overrides(self):
        self.assertEqual(dependencies.blockers(["unittest2"]), frozenset())


if __name__ == '__main__':
    unittest.main()
