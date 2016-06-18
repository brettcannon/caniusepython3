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

from caniusepython3 import dependencies
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


class BlockingDependenciesTests(unittest.TestCase):

    @mock.patch('caniusepython3.dependencies.dependencies')
    def test_recursion(self, dependencies_mock):
        deps = {'a': ['b'], 'b': ['a']}
        dependencies_mock.side_effect = lambda name: deps[name]
        got = dependencies.blocking_dependencies(['a'], {})
        self.assertEqual(frozenset(), got)

    def test_blocking_dependencies_locators_fails(self):
        # Testing the work around for //bitbucket.org/pypa/distlib/issue/59/ .
        with mock.patch.object(distlib.locators, 'locate') as locate_mock:
            py3 = {'py3_project': ''}
            breaking_project = 'test_project'
            locate_mock.side_effect = AttributeError()
            got = dependencies.blocking_dependencies([breaking_project], py3)
            # If you'd like to test that a message is logged we can use
            # testfixtures.LogCapture or stdout redirects.


class NetworkTests(unittest.TestCase):

    def test_blocking_dependencies(self):
        got = dependencies.blocking_dependencies(['mozinfo'], {})
        want = frozenset([('mozfile', 'mozinfo')])
        self.assertEqual(frozenset(got), want)

    def test_dependencies(self):
        got = dependencies.dependencies('pastescript')
        self.assertEqual(set(got), frozenset(['six', 'pastedeploy', 'paste']))

    def test_dependencies_no_project(self):
        got = dependencies.dependencies('sdflksjdfsadfsadfad')
        self.assertIsNone(got)

    def test_blocking_dependencies_no_project(self):
        got = dependencies.blocking_dependencies(['asdfsadfdsfsdffdfadf'], {})
        self.assertEqual(got, frozenset())

    def test_top_level_project_normalization(self):
        py3 = {'wsgi_intercept': ''}
        abnormal_name = 'WSGI-intercept'  # Note dash instead of underscore.
        got = dependencies.blocking_dependencies([abnormal_name], py3)
        self.assertEqual(got, frozenset())

if __name__ == '__main__':
    unittest.main()
