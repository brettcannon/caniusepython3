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
import tempfile
import unittest
try:
    from unittest import mock
except ImportError:
    import mock


EXAMPLE_REQUIREMENTS = """
# From
#  http://www.pip-installer.org/en/latest/reference/pip_install.html#requirement-specifiers
# but without the quotes for shell protection.
FooProject >= 1.2
Fizzy [foo, bar]
PickyThing<1.6,>1.9,!=1.9.6,<2.0a0,==2.4c1
Hello
"""

EXAMPLE_METADATA = """Metadata-Version: 1.2
Name: CLVault
Version: 0.5
Summary: Command-Line utility to store and retrieve passwords
Home-page: http://bitbucket.org/tarek/clvault
Author: Tarek Ziade
Author-email: tarek@ziade.org
License: PSF
Keywords: keyring,password,crypt
Requires-Dist: foo; sys.platform == 'okook'
Requires-Dist: bar
Platform: UNKNOWN
"""

class CLITests(unittest.TestCase):

    expected_requirements = frozenset(['FooProject', 'Fizzy', 'PickyThing',
                                       'Hello'])
    expected_metadata = frozenset(['foo', 'bar'])

    def test_requirements(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_REQUIREMENTS)
            file.flush()
            got = ciu.projects_from_requirements(file.name)
        self.assertEqual(set(got), self.expected_requirements)

    def test_metadata(self):
        got = ciu.projects_from_metadata(EXAMPLE_METADATA)
        self.assertEqual(set(got), self.expected_metadata)

    def test_cli_for_requirements(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_REQUIREMENTS)
            file.flush()
            args = ['--requirements', file.name]
            got = ciu.projects_from_cli(args)
        self.assertEqual(set(got), self.expected_requirements)

    def test_cli_for_metadata(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_METADATA)
            file.flush()
            args = ['--metadata', file.name]
            got = ciu.projects_from_cli(args)
        self.assertEqual(set(got), self.expected_metadata)

    def test_cli_for_projects(self):
        args = ['--projects', 'foo,bar']
        got = ciu.projects_from_cli(args)
        self.assertEqual(set(got), frozenset(['foo', 'bar']))

    def test_message_plural(self):
        blockers = [['A'], ['B']]
        messages = ciu.message(blockers)
        self.assertEqual(2, len(messages))
        want = 'You need 2 projects to transition to Python 3.'
        self.assertEqual(messages[0], want)
        want = ('Of those 2 projects, 2 have no direct dependencies blocking '
                'their transition:')
        self.assertEqual(messages[1], want)

    def test_message_plural(self):
        blockers = [['A']]
        messages = ciu.message(blockers)
        self.assertEqual(2, len(messages))
        want = 'You need 1 project to transition to Python 3.'
        self.assertEqual(messages[0], want)
        want = ('Of that 1 project, 1 has no direct dependencies blocking '
                'its transition:')
        self.assertEqual(messages[1], want)

    def test_message_no_blockers(self):
        messages = ciu.message([])
        self.assertEqual(
            ['You have 0 projects blocking you from using Python 3!'],
            messages)

    def test_pprint_blockers(self):
        simple = [['A']]
        fancy = [['A', 'B']]
        nutty = [['A', 'B', 'C']]
        repeated = [['A', 'C'], ['B']]  # Also tests sorting.
        got = ciu.pprint_blockers(simple)
        self.assertEqual(list(got), ['A'])
        got = ciu.pprint_blockers(fancy)
        self.assertEqual(list(got), ['A (which is blocking B)'])
        got = ciu.pprint_blockers(nutty)
        self.assertEqual(list(got),
                         ['A (which is blocking B, which is blocking C)'])
        got = ciu.pprint_blockers(repeated)
        self.assertEqual(list(got), ['B', 'A (which is blocking C)'])


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

    def test_all_py3_projects(self):
        projects = ciu.all_py3_projects()
        if hasattr(self, 'assertGreater'):
            self.assertGreater(len(projects), 3000)
        else:
            self.assertTrue(len(projects) > 3000)
        self.assertTrue(all(project == project.lower() for project in projects))
        self.assertTrue(ciu.OVERRIDES.issubset(projects))

    @mock.patch('sys.stdout', io.StringIO())
    def test_e2e(self):
        # Make sure at least one project that will never be in Python 3 is
        # included.
        ciu.main(['--projects', 'numpy,scipy,matplotlib,ipython,unittest2'])


if __name__ == '__main__':
    unittest.main()
