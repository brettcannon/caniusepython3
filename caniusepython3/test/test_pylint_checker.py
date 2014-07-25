from __future__ import absolute_import

import io
import sys
import tokenize

from astroid import test_utils
from pylint import testutils

from caniusepython3 import pylint_checker as checker
from caniusepython3.test import unittest


class SixCheckerTest(testutils.CheckerTestCase):

    CHECKER_CLASS = checker.SixChecker

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_print_statement(self):
        node = test_utils.extract_node('print "Hello, World!" #@')
        with self.assertAddsMessages(testutils.Message('print-statement', node=node)):
            self.checker.visit_print(node)

    def test_method_false_positive(self):
        node = test_utils.extract_node("""
        def next():  #@
            pass""")
        with self.assertNoMessages():
            self.checker.visit_function(node)

    def test_getslice_method(self):
        node = test_utils.extract_node("""
        class Foo(object):
            def __getslice__(self, i, j):  #@
                pass""")
        with self.assertAddsMessages(testutils.Message('getslice-method', node=node)):
            self.checker.visit_function(node)

    def test_setslice_method(self):
        node = test_utils.extract_node("""
        class Foo(object):
            def __setslice__(self, i, j, value):  #@
                pass""")
        with self.assertAddsMessages(testutils.Message('setslice-method', node=node)):
            self.checker.visit_function(node)

    def test_cmp_method(self):
        node = test_utils.extract_node("""
        class Foo(object):
            def __cmp__(self, other):  #@
                pass""")
        with self.assertAddsMessages(testutils.Message('cmp-method', node=node)):
            self.checker.visit_function(node)

    def test_coerce_method(self):
        node = test_utils.extract_node("""
        class Foo(object):
            def __coerce__(self, other):  #@
                pass""")
        with self.assertAddsMessages(testutils.Message('coerce-method', node=node)):
            self.checker.visit_function(node)

    def test_unicode_method(self):
        node = test_utils.extract_node("""
        class Foo(object):
            def __unicode__(self, other):  #@
                pass""")
        with self.assertAddsMessages(testutils.Message('unicode-method', node=node)):
            self.checker.visit_function(node)

    def test_cmp_method(self):
        node = test_utils.extract_node("""
        class Foo(object):
            def next(self):  #@
                pass""")
        with self.assertAddsMessages(testutils.Message('next-method', node=node)):
            self.checker.visit_function(node)

    def test_builtin_false_positive(self):
        node = test_utils.build_module('long = int; long  #@')
        with self.assertNoMessages():
            self.checker.visit_name(node)

    def check_not_builtin(self, builtin_name, message):
        node = test_utils.extract_node(builtin_name + '  #@')
        with self.assertAddsMessages(testutils.Message(message, node=node)):
            self.checker.visit_name(node)

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_buffer_builtin(self):
        self.check_not_builtin('buffer', 'buffer-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_apply_builtin(self):
        self.check_not_builtin('apply', 'apply-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_cmp_builtin(self):
        self.check_not_builtin('cmp', 'cmp-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_file_builtin(self):
        self.check_not_builtin('file', 'file-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_raw_input_builtin(self):
        self.check_not_builtin('raw_input', 'raw_input-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_long_builtin(self):
        self.check_not_builtin('long', 'long-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_coerce_builtin(self):
        self.check_not_builtin('coerce', 'coerce-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_execfile_builtin(self):
        self.check_not_builtin('execfile', 'execfile-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_xrange_builtin(self):
        self.check_not_builtin('xrange', 'xrange-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_unicode_builtin(self):
        self.check_not_builtin('unicode', 'unicode-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_StandardError(self):
        self.check_not_builtin('StandardError', 'standarderror-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_map_builtin(self):
        self.check_not_builtin('map', 'map-builtin')

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_zip_builtin(self):
        self.check_not_builtin('zip', 'zip-builtin')

    def test_division(self):
        node = test_utils.extract_node('3 / 2  #@')
        with self.assertAddsMessages(testutils.Message('division', node=node)):
            self.checker.visit_binop(node)

    def test_division_with_future_statement(self):
        module = test_utils.build_module('from __future__ import division; 3 / 2')
        with self.assertNoMessages():
            self.walk(module)

    def test_floor_division(self):
        node = test_utils.extract_node(' 3 // 2  #@')
        with self.assertNoMessages():
            self.checker.visit_binop(node)

    def test_division_by_float(self):
        left_node = test_utils.extract_node('3.0 / 2 #@')
        right_node = test_utils.extract_node(' 3 / 2.0  #@')
        with self.assertNoMessages():
            for node in (left_node, right_node):
                self.checker.visit_binop(node)

    def test_relative_import(self):
        node = test_utils.extract_node('import string  #@')
        with self.assertAddsMessages(testutils.Message('no-absolute-import', node=node)):
            self.checker.visit_import(node)

    def test_relative_from_import(self):
        node = test_utils.extract_node('from os import path  #@')
        with self.assertAddsMessages(testutils.Message('no-absolute-import', node=node)):
            self.checker.visit_import(node)

    def test_absolute_import(self):
        module_import = test_utils.build_module('from __future__ import absolute_import; import os')
        module_from = test_utils.build_module('from __future__ import absolute_import; from os import path')
        with self.assertNoMessages():
            for module in (module_import, module_from):
                self.walk(module)


class UnicodeCheckerTest(testutils.CheckerTestCase):

    CHECKER_CLASS = checker.UnicodeChecker

    def tokenize(self, source):
        return tokenize.generate_tokens(io.StringIO(source).readline)

    def test_bytes_okay(self):
        tokens = self.tokenize(u"b'abc'")
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_unicode_okay(self):
        tokens = self.tokenize(u"u'abc'")
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_native_string(self):
        arg = u"val = 'abc'"
        tokens = self.tokenize(arg)
        with self.assertAddsMessages(testutils.Message('native-string', line=1)):
            self.checker.process_tokens(tokens)

    def test_future_unicode(self):
        arg = u"from __future__ import unicode_literals; val = 'abc'"
        tokens = self.tokenize(arg)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_after_module_docstring(self):
        module = u'"""Module docstring"""\nfrom __future__ import unicode_literals'
        tokens = self.tokenize(module)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_after_shebang_and_module_docstring(self):
        module = u'#! /usr/bin/python2.7\n"""Module docstring"""\nfrom __future__ import unicode_literals'
        tokens = self.tokenize(module)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)


class SyntaxCheckerTest(testutils.CheckerTestCase):

    CHECKER_CLASS = checker.SyntaxChecker

    def tokenize(self, source):
        return tokenize.generate_tokens(io.StringIO(source).readline)

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_py2_octal_literal(self):
        tokens = self.tokenize(u'012')
        with self.assertAddsMessages(testutils.Message('octal-literal', line=1)):
            self.checker.process_tokens(tokens)

    def test_py3_octal_literal(self):
        tokens = self.tokenize(u'0o12')
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_long_L(self):
        tokens = self.tokenize(u'123L')
        with self.assertAddsMessages(testutils.Message('long-literal', line=1)):
            self.checker.process_tokens(tokens)

    @unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')
    def test_long_l(self):
        tokens = self.tokenize(u'123l')
        with self.assertAddsMessages(testutils.Message('long-literal', line=1)):
            self.checker.process_tokens(tokens)


if __name__ == '__main__':
    #from logilab.common.testlib import unittest_main
    #unittest_main()
    import unittest
    unittest.main()
