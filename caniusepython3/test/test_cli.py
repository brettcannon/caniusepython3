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

import caniusepython3.__main__ as ciu_main
from caniusepython3 import projects, pypi
from caniusepython3.test import mock, unittest, skip_pypi_timeouts

import io
import logging
import tempfile


EXAMPLE_REQUIREMENTS = """
# From
#  http://www.pip-installer.org/en/latest/reference/pip_install.html#requirement-specifiers
# but without the quotes for shell protection.
Foo.Project \
    >= 1.2
Fizzy [foo, bar]
PickyThing<1.6,>1.9,!=1.9.6,<2.0a0,==2.4c1
Hello
-e git+https://github.com/brettcannon/caniusepython3#egg=caniusepython3
file:../caniusepython3#egg=caniusepython3
# Docs say to specify an #egg argument, but apparently it's optional.
file:../../lib/project
"""

EXAMPLE_EXTRA_REQUIREMENTS = """
testing-stuff
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
Requires-Dist: bar.baz
Platform: UNKNOWN
"""

EXAMPLE_EXTRA_METADATA = """Metadata-Version: 1.2
Name: ExtraTest
Version: 0.5
Summary: Just for testing
Home-page: nowhere
Author: nobody
License: Apache
Requires-Dist: baz
"""


class CLITests(unittest.TestCase):

    expected_requirements = frozenset(['foo-project', 'fizzy', 'pickything',
                                       'hello'])
    expected_extra_requirements = frozenset(['testing-stuff'])
    expected_metadata = frozenset(['foo', 'bar-baz'])
    expected_extra_metadata = frozenset(['baz'])

    def setUp(self):
        log = logging.getLogger('ciu')
        self._prev_log_level = log.getEffectiveLevel()
        logging.getLogger('ciu').setLevel(1000)

    def tearDown(self):
        logging.getLogger('ciu').setLevel(self._prev_log_level)

    def test_requirements(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_REQUIREMENTS)
            file.flush()
            got = projects.projects_from_requirements([file.name])
        self.assertEqual(set(got), self.expected_requirements)

    def test_multiple_requirements_files(self):
        with tempfile.NamedTemporaryFile('w') as f1:
            f1.write(EXAMPLE_REQUIREMENTS)
            f1.flush()
            with tempfile.NamedTemporaryFile('w') as f2:
                f2.write(EXAMPLE_EXTRA_REQUIREMENTS)
                f2.flush()
                got = projects.projects_from_requirements([f1.name, f2.name])
        want = self.expected_requirements.union(self.expected_extra_requirements)
        self.assertEqual(set(got), want)

    def test_metadata(self):
        got = projects.projects_from_metadata([EXAMPLE_METADATA])
        self.assertEqual(set(got), self.expected_metadata)

    def test_multiple_metadata(self):
        got = projects.projects_from_metadata([EXAMPLE_METADATA,
                                               EXAMPLE_EXTRA_METADATA])
        want = self.expected_metadata.union(self.expected_extra_metadata)
        self.assertEqual(set(got), want)

    def test_cli_for_requirements(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_REQUIREMENTS)
            file.flush()
            args = ['--requirements', file.name]
            parsed = ciu_main.arguments_from_cli(args)
            got = ciu_main.projects_from_parsed(parsed)
        self.assertEqual(set(got), self.expected_requirements)

    def test_excluding_requirements(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_REQUIREMENTS)
            file.flush()
            args = ['--requirements', file.name, '--exclude', 'pickything']
            parsed = ciu_main.arguments_from_cli(args)
            got = ciu_main.projects_from_parsed(parsed)
        expected_requirements = set(self.expected_requirements)
        expected_requirements.remove('pickything')
        self.assertNotIn('pickything', set(got))
        self.assertEqual(set(got), expected_requirements)

    def test_cli_for_metadata(self):
        with tempfile.NamedTemporaryFile('w') as file:
            file.write(EXAMPLE_METADATA)
            file.flush()
            args = ['--metadata', file.name]
            parsed = ciu_main.arguments_from_cli(args)
            got = ciu_main.projects_from_parsed(parsed)
        self.assertEqual(set(got), self.expected_metadata)

    def test_cli_for_projects(self):
        args = ['--projects', 'foo', 'bar.baz']
        parsed = ciu_main.arguments_from_cli(args)
        got = ciu_main.projects_from_parsed(parsed)
        self.assertEqual(set(got), frozenset(['foo', 'bar-baz']))

    def test_cli_for_index(self):
        args = ['--projects', 'foo', 'bar.baz',
                '--index', 'some-url']
        parsed = ciu_main.arguments_from_cli(args)
        self.assertEqual(parsed.index, 'some-url')

    def test_cli_for_index_default(self):
        args = ['--projects', 'foo', 'bar.baz']
        parsed = ciu_main.arguments_from_cli(args)
        self.assertEqual(parsed.index, 'https://pypi.org/pypi')

    def test_message_plural(self):
        blockers = [['A'], ['B']]
        messages = ciu_main.message(blockers)
        self.assertEqual(2, len(messages))
        want = 'You need 2 projects to transition to Python 3.'
        self.assertEqual(messages[0], want)
        want = ('Of those 2 projects, 2 have no direct dependencies blocking '
                'their transition:')
        self.assertEqual(messages[1], want)

    def test_message_singular(self):
        blockers = [['A']]
        messages = ciu_main.message(blockers)
        self.assertEqual(2, len(messages))
        want = 'You need 1 project to transition to Python 3.'
        self.assertEqual(messages[0], want)
        want = ('Of that 1 project, 1 has no direct dependencies blocking '
                'its transition:')
        self.assertEqual(messages[1], want)

    @mock.patch('sys.stdout', autospec=True)
    def test_message_no_blockers_flair_on_utf8_terminal(self, mock_stdout):
        mock_stdout.encoding = 'UTF-8'
        messages = ciu_main.message([])
        expected = ['\U0001f389  You (potentially) have 0 projects blocking you from using Python 3!']
        self.assertEqual(expected, messages)

    @mock.patch('sys.stdout', autospec=True)
    def test_message_no_blockers(self, mock_stdout):
        mock_stdout.encoding = None
        messages = ciu_main.message([])
        expected = ['You (potentially) have 0 projects blocking you from using Python 3!']
        self.assertEqual(expected, messages)

    def test_pprint_blockers(self):
        simple = [['A']]
        fancy = [['A', 'B']]
        nutty = [['A', 'B', 'C']]
        repeated = [['A', 'C'], ['B']]  # Also tests sorting.
        got = ciu_main.pprint_blockers(simple)
        self.assertEqual(list(got), ['A'])
        got = ciu_main.pprint_blockers(fancy)
        self.assertEqual(list(got), ['A (which is blocking B)'])
        got = ciu_main.pprint_blockers(nutty)
        self.assertEqual(list(got),
                         ['A (which is blocking B, which is blocking C)'])
        got = ciu_main.pprint_blockers(repeated)
        self.assertEqual(list(got), ['B', 'A (which is blocking C)'])

    @mock.patch('argparse.ArgumentParser.error')
    def test_projects_must_be_specified(self, parser_error):
        ciu_main.arguments_from_cli([])
        self.assertEqual(
            mock.call("Missing 'requirements', 'metadata', or 'projects'"),
            parser_error.call_args)

    def test_verbose_output(self):
        ciu_main.arguments_from_cli(['-v', '-p', 'ipython'])
        self.assertTrue(logging.getLogger('ciu').isEnabledFor(logging.INFO))

    @mock.patch('caniusepython3.dependencies.blockers',
                lambda projects, index_url: ['blocker'])
    def test_nonzero_return_code(self):
        args = ['--projects', 'foo', 'bar.baz']
        with self.assertRaises(SystemExit) as context:
            ciu_main.main(args=args)
        self.assertNotEqual(context.exception.code, 0)


#@unittest.skip('faster testing')
class NetworkTests(unittest.TestCase):

    @skip_pypi_timeouts
    @mock.patch('sys.stdout', io.StringIO())
    def test_e2e(self):
        # Make sure at least one project that will never be in Python 3 is
        # included.
        args = '--projects', 'numpy', 'scipy', 'matplotlib', 'ipython', 'paste'
        ciu_main.main(args)

    @skip_pypi_timeouts
    @mock.patch('sys.stdout', io.StringIO())
    def test_e2e_with_specified_index(self):
        args = '--projects', 'paste', '--index', pypi.PYPI_INDEX_URL
        ciu_main.main(args)


if __name__ == '__main__':
    unittest.main()
