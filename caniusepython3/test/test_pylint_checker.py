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
from __future__ import absolute_import, unicode_literals

from caniusepython3.test import unittest

ALL_GOOD = True
try:
    import io
    import sys
    import tokenize

    from astroid import test_utils
    from pylint import testutils
    from pylint.testutils import CheckerTestCase

    from caniusepython3.pylint_checker import StrictPython3Checker, UnicodeChecker
except (ImportError, SyntaxError):
    ALL_GOOD = False
    CheckerTestCase = unittest.TestCase
    StrictPython3Checker = None
    UnicodeChecker = None


thorough_unicode_test = """'''Module Docstring'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def awesome():
        print("awesome")
"""


def new_enough(test):
    return unittest.skipIf(not ALL_GOOD,
            'Pylint requires Python 2.7/3.3 or newer')(test)

def python2_only(test):
    """Decorator for any tests that will fail under Python 3."""
    return unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')(test)

@new_enough
class StrictPython3CheckerTest(CheckerTestCase):

    CHECKER_CLASS = StrictPython3Checker

    def check_not_builtin(self, builtin_name, message):
        node = test_utils.extract_node(builtin_name + '  #@')
        with self.assertAddsMessages(testutils.Message(message, node=node)):
            self.checker.visit_name(node)

    @python2_only
    def test_open_builtin(self):
        self.check_not_builtin('open', 'open-builtin')

    def test_dict_comprehension(self):
        node = test_utils.extract_node('{e:"1" for e in ["one", "two"]} #@')
        with self.assertNoMessages():
            self.checker.visit_name(node)

@new_enough
class UnicodeCheckerTest(CheckerTestCase):

    CHECKER_CLASS = UnicodeChecker

    def tokenize(self, source):
        return tokenize.generate_tokens(io.StringIO(source).readline)

    def test_bytes_okay(self):
        tokens = self.tokenize("b'abc'")
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_unicode_okay(self):
        tokens = self.tokenize("u'abc'")
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_native_string(self):
        arg = "val = 'abc'"
        tokens = self.tokenize(arg)
        with self.assertAddsMessages(testutils.Message('native-string', line=1)):
            self.checker.process_tokens(tokens)

    def test_future_unicode(self):
        arg = "from __future__ import unicode_literals; val = 'abc'"
        tokens = self.tokenize(arg)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_after_module_docstring(self):
        module = '"""Module docstring"""\nfrom __future__ import unicode_literals'
        tokens = self.tokenize(module)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_after_shebang_and_module_docstring(self):
        module = '#! /usr/bin/python2.7\n"""Module docstring"""\nfrom __future__ import unicode_literals'
        tokens = self.tokenize(module)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_thoroughly(self):
        tokens = self.tokenize(thorough_unicode_test)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)


if __name__ == '__main__':
    import unittest
    unittest.main()
