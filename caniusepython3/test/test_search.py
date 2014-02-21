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

import io
import unittest


class NameTests(unittest.TestCase):

    def test_simple(self):
        want = 'simple-name_with.everything-separator_known'
        got = ciu.just_name(want)
        self.assertEqual(got, want)

    def test_requirements(self):
        want = 'project.name'
        got = ciu.just_name(want + '>=2.0.1')
        self.assertEqual(got, want)

    def test_bad_requirements(self):
        # From the OpenStack requirements file:
        # https://raw2.github.com/openstack/requirements/master/global-requirements.txt
        want = 'warlock'
        got = ciu.just_name(want + '>1.01<2')
        self.assertEqual(got, want)

    def test_metadata(self):
        want = 'foo'
        got = ciu.just_name("foo; sys.platform == 'okook'")
        self.assertEqual(got, want)


class OverridesTests(unittest.TestCase):

    def test_all_lowercase(self):
        for name in ciu.overrides():
            self.assertEqual(name, name.lower())


class GraphResolutionTests(unittest.TestCase):

    def test_all_projects_okay(self):
        # A, B, and C are fine on their own.
        self.assertEqual(set(), ciu.reasons_to_paths({}))

    def test_leaf_okay(self):
        # A -> B where B is okay.
        reasons = {'A': None}
        self.assertEqual(frozenset([('A',)]), ciu.reasons_to_paths(reasons))

    def test_leaf_bad(self):
        # A -> B -> C where all projects are bad.
        reasons = {'A': None, 'B': 'A', 'C': 'B'}
        self.assertEqual(frozenset([('C', 'B', 'A')]),
                         ciu.reasons_to_paths(reasons))


#@unittest.skip('faster testing')
class NetworkTests(unittest.TestCase):

    def py3_classifiers(self):
        key_classifier = 'Programming Language :: Python :: 3'
        classifiers = frozenset(ciu.py3_classifiers())
        if hasattr(self, 'assertIn'):
            self.asssertIn(key_classifier, classifiers)
        else:
            self.assertTrue(key_classifier in classifiers)
        if hasattr(self, 'assertGreaterEqual'):
            self.assertGreaterEqual(len(classifiers), 5)
        else:
            self.assertTrue(len(classifiers) >= 5)
        for classifier in classifiers:
            self.assertTrue(classifier.startswith(key_classifier))


    def test_all_py3_projects(self):
        projects = ciu.all_py3_projects()
        if hasattr(self, 'assertGreater'):
            self.assertGreater(len(projects), 3000)
        else:
            self.assertTrue(len(projects) > 3000)
        self.assertTrue(all(project == project.lower() for project in projects))
        self.assertTrue(ciu.overrides().issubset(projects))

    def test_blocking_dependencies(self):
        got = ciu.blocking_dependencies(['unittest2'], {})
        want = set([('unittest2',)])
        self.assertEqual(got, want)


if __name__ == '__main__':
    unittest.main()
