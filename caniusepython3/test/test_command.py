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

from distutils import dist
import unittest

class RequiresTests(unittest.TestCase):

    def cmd(self, requires):
        return command.Command(dist.Distribution(requires))


    def cmd_test(self, requirements):
        requires = {requirements: ['pip']}
        cmd = self.cmd(requires)
        got = cmd._dependencies()
        self.assertEqual(frozenset(got), frozenset(['pip']))

    def test_install_requires(self):
        self.cmd_test('install_requires')

    def test_tests_require(self):
        self.cmd_test('tests_require')

    def test_extras_require(self):
        cmd = self.cmd({'extras_require': {'testing': ['pip']}})
        got = frozenset(cmd._dependencies())
        self.assertEqual(got, frozenset(['pip']))
