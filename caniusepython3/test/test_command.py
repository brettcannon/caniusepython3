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

from caniusepython3 import command
from caniusepython3.test import unittest, skip_pypi_timeouts, mock

import setuptools  # To suppress a warning.
from distutils import dist

def make_command(requires):
    return command.Command(dist.Distribution(requires))

class RequiresTests(unittest.TestCase):

    def verify_cmd(self, requirements):
        requires = {requirements: ['pip']}
        cmd = make_command(requires)
        got = cmd._dependencies()
        self.assertEqual(frozenset(got), frozenset(['pip']))
        return cmd

    def test_install_requires(self):
        self.verify_cmd('install_requires')

    def test_tests_require(self):
        self.verify_cmd('tests_require')

    def test_extras_require(self):
        cmd = make_command({'extras_require': {'testing': ['pip']}})
        got = frozenset(cmd._dependencies())
        self.assertEqual(got, frozenset(['pip']))

    @mock.patch('caniusepython3.dependencies.blockers',
                lambda projects, index_url: ['blocker'])
    def test_nonzero_return_code(self):
        cmd = make_command({'install_requires': ['pip']})
        with self.assertRaises(SystemExit) as context:
            cmd.run()
        self.assertNotEqual(context.exception.code, 0)


class OptionsTests(unittest.TestCase):

    def test_finalize_options(self):
        # Don't expect anything to happen.
        make_command({}).finalize_options()


class NetworkTests(unittest.TestCase):

    @skip_pypi_timeouts
    def test_run(self):
        make_command({'install_requires': ['pip']}).run()
