"""Pylint checker to enforce Python 2/3 compatible syntax.

See the documentation for what checkers pylint includes by default
which compliment this file.
"""
from __future__ import absolute_import, print_function

import symbol
import token
import tokenize

import astroid
from astroid import nodes
from pylint import checkers, interfaces
from pylint.checkers import utils

# http://python3porting.com/differences.html
## Straight-forward ########################
### round() different
####-------------------
### No dict.iter*()
### No list.sort(cmp=)
## Scoping #################################
### io.open() over open()
### no sorted(cmp=)
####-------------------
### list(filter()) or future_builtins.filter()
### No exception object escaping `except` scope
### No listcomp variable escaping
## Don't know how to catch #################
### indexing bytes

# Python 2.5
## codecs.open over open()/file()

class SixChecker(checkers.BaseChecker):

    __implements__ = interfaces.IAstroidChecker

    name = 'six'
    msgs = {
        # Errors for what will syntactically break in Python 3, warnings for
        # everything else.
        'E6001': ('Use of a print statement',
                  'print-statement',
                  'Used when a print statement is found '
                  '(invalid syntax in Python 3)',
                  {'maxversion': (3, 0)}),
        'E6002': ('Use of an exec statement',
                  'exec-statement',
                  'Used when an exec statement is found'
                  '(invalid syntax in Python 3)',
                  {'maxversion': (3, 0)}),
        'E6003': ('Parameter unpacking specified',
                  'parameter-unpacking',
                  'Used when parameter unpacking is specified for a function'
                  "(Python 3 doesn't allow it)",
                  {'maxversion': (3, 0)}),
        'W6001': ('__getslice__ defined',
                  'getslice-method',
                  'Used when a __getslice__ method  is defined '
                  '(unused in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6002': ('__setslice__ defined',
                  'setslice-method',
                  'Used when a __setslice__ method is defined '
                  '(unused in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6003': ('__cmp__ defined',
                  'cmp-method',
                  'Used when a __cmp__ method is defined '
                  '(unused in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6004': ('__coerce__ defined',
                  'coerce-method',
                  'Used when a __coerce__ method is defined '
                  '(unused in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6005': ('__unicode__ defined',
                  'unicode-method',
                  'Used when a __unicode__ method is defined '
                  '(renamed __str__ in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6006': ('next defined',
                  'next-method',
                  "Used when a 'next' method is defined "
                  '(renamed __next__ in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6007': ('buffer built-in referenced',
                  'buffer-builtin',
                  'Used when the buffer() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6008': ('apply built-in referenced',
                  'apply-builtin',
                  'Used when the apply() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6009': ('cmp built-in referenced',
                  'cmp-builtin',
                  'Used when the cmp() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6010': ('file built-in referenced',
                  'file-builtin',
                  'Used when the file() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6011': ('raw_input built-in referenced',
                  'raw_input-builtin',
                  'Used when the raw_input() built-in function is referenced '
                  "(renamed 'input' in Python 3)",
                  {'maxversion': (3, 0)}),
        'W6012': ('long built-in referenced',
                  'long-builtin',
                  'Used when the long() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6013': ('coerce built-in referenced',
                  'coerce-builtin',
                  'Used when the coerce() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6014': ('execfile built-in referenced',
                  'execfile-builtin',
                  'Used when the execfile() built-in function is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6015': ('xrange built-in referenced',
                  'xrange-builtin',
                  'Used when the xrange() built-in function is referenced '
                  "(renamed 'range' in Python 3)",
                  {'maxversion': (3, 0)}),
        'W6016': ('unicode built-in referenced',
                  'unicode-builtin',
                  'Used when the unicode() built-in function is referenced '
                  "(renamed 'str' in Python 3)",
                  {'maxversion': (3, 0)}),
        'W6017': ('StandardError built-in referenced',
                  'standarderror-builtin',
                  'Used when the StandardError built-in exception is referenced '
                  '(removed in Python 3)',
                  {'maxversion': (3, 0)}),
        'W6018': ('map built-in referenced',
                  'map-builtin',
                  'Used when the map built-in function is referenced '
                  '(semantics different in Python 3; '
                  'use future_builtins.map)',
                  {'maxversion': (3, 0)}),
        'W6019': ('zip built-in referenced',
                  'zip-builtin',
                  'Used when the zip built-in function is referenced '
                  '(semantics different in Python 3; '
                  'use future_builtins.zip)',
                  {'maxversion': (3, 0)}),
        'W6020': ('division w/o __future__ statement',
                  'division',
                  'Used for non-floor division w/o a float literal or '
                  '``from __future__ import division``'
                  '(Python 3 returns a float for int division unconditionally)',
                  {'maxversion': (3, 0)}),
        'W6021': ('import w/o ``from __future__ import absolute_import``',
                  'no-absolute-import',
                  'Used when an import is performed w/o'
                  '``from __future__ import absolute_import``',
                  {'maxversion': (3, 0)}),
        'W6022': ('__metaclass__ assigned',
                  'metaclass-attribute',
                  'Assignment to the __metaclass__ attribute'
                  "(Python 3 sets the metaclass in the class' parameter list)",
                  {'maxversion': (3, 0)}),
    }

    def __init__(self, *args, **kwargs):
        self._future_division = False
        self._future_absolute_import = False
        super(SixChecker, self).__init__(*args, **kwargs)

    @utils.check_messages('print-statement')
    def visit_print(self, node):
        self.add_message('print-statement', node=node)

    @utils.check_messages('exec-statement')
    def visit_exec(self, node):
        self.add_message('exec-statement', node=node)

    @utils.check_messages('no-absolute-import')
    def visit_from(self, node):
        if node.modname == u'__future__' :
            for name, _ in node.names:
                if name == u'division':
                    self._future_division = True
                elif name == u'absolute_import':
                    self._future_absolute_import = True
        elif not self._future_absolute_import:
            self.add_message('no-absolute-import', node=node)

    @utils.check_messages('no-absolute-import')
    def visit_import(self, node):
        if not self._future_absolute_import:
            self.add_message('no-absolute-import', node=node)

    @utils.check_messages('division')
    def visit_binop(self, node):
        if not self._future_division and node.op == u'/':
            for arg in (node.left, node.right):
                if isinstance(arg, astroid.Const) and isinstance(arg.value, float):
                    break
            else:
                self.add_message('division', node=node)

    def visit_function(self, node):
        bad_methods = {'__getslice__': 'getslice-method',
                       '__setslice__': 'setslice-method',
                       '__cmp__': 'cmp-method',
                       '__coerce__': 'coerce-method',
                       '__unicode__': 'unicode-method',
                       'next': 'next-method'}
        if node.is_method() and node.name in bad_methods:
            self.add_message(bad_methods[node.name], node=node)

    @utils.check_messages('parameter-unpacking')
    def visit_arguments(self, node):
        for arg in node.args:
            if isinstance(arg, nodes.Tuple):
                self.add_message('parameter-unpacking', node=arg)

    def visit_name(self, node):
        if node.lookup(node.name)[0].name == '__builtin__':
            bad_builtins = {'buffer': 'buffer-builtin',
                            'apply': 'apply-builtin',
                            'cmp': 'cmp-builtin',
                            'file': 'file-builtin',
                            'raw_input': 'raw_input-builtin',
                            'long': 'long-builtin',
                            'coerce': 'coerce-builtin',
                            'execfile': 'execfile-builtin',
                            'xrange': 'xrange-builtin',
                            'unicode': 'unicode-builtin',
                            'StandardError': 'standarderror-builtin',
                            'map': 'map-builtin',  # Technically only care when used.
                            'zip': 'zip-builtin',  # Technically only care when used.
                           }
            if node.name in bad_builtins:
                self.add_message(bad_builtins[node.name], node=node)

    @utils.check_messages('metaclass-attribute')
    def visit_assign(self, node):
        for target in node.targets:
            if u'__metaclass__' == target.name:
                self.add_message('metaclass-attribute', node=node)


class UnicodeChecker(checkers.BaseTokenChecker):

    __implements__ = interfaces.ITokenChecker

    name = 'unicode'
    msgs = {
        'W6100': ('native string literal',
                  'native-string',
                  'Used when a string has no b/u prefix and '
                  '``from __future__ import unicode_literals`` not found '
                  '(strings w/ no prefix in Python 3 are Unicode)',
                  {'maxversion': (3, 0)}),
    }

    def process_tokens(self, tokens):
        # Module docstring can be a native string.
        # Also use as a flag to notice when __future__ statements are no longer
        # valid to avoid wasting time checking every NAME token
        # (which is < STRING).
        module_start = True
        line_num = 1
        for type_, val, start, end, line in tokens:
            if type_ in (token.NEWLINE, tokenize.NL):
                line_num += 1
            # Anything else means we are past the first string in the module,
            # any comments (e.g. shebang), and no more __future__ statements
            # are possible.
            if type_ > token.STRING and type_ < token.N_TOKENS:
                module_start = False
            elif type_ == token.STRING:
                line_num += val.count('\n')
                if not module_start and not val.startswith(('u', 'b')):
                    self.add_message('native-string', line=line_num)
            elif module_start and type_ == token.NAME:
                if len(line) >= 39:  # Fast-fail check
                    if u'__future__' in line and u'unicode_literals' in line:
                        return


class SyntaxChecker(checkers.BaseTokenChecker):

    __implements__ = interfaces.ITokenChecker

    name = 'six'
    msgs = {
        'E6101': ('octal literal',
                  'octal-literal',
                  'Used when a octal literal w/ ``0`` prefix is defined '
                  '(Python 3 uses ``0o``)',
                  {'maxversion': (3, 0)}),
        'E6102': ('long literal',
                  'long-literal',
                  'Used when a long literal is defined '
                  '(Python 3 unified int and long)',
                  {'maxversion': (3, 0)}),
    }

    def process_tokens(self, tokens):
        line_num = 1
        for type_, val, start, end, line in tokens:
            if type_ in (token.NEWLINE, tokenize.NL):
                line_num += 1
            elif type_ == token.STRING:
                line_num += val.count('\n')
            elif type_ == token.NUMBER and len(val) > 1:
                if val.startswith(u'0'):
                    if not val.startswith(u'0o'):
                        self.add_message('octal-literal', line=line_num)
                elif val.endswith((u'L', u'l')):
                    self.add_message('long-literal', line=line_num)


def register(linter):
    linter.register_checker(SixChecker(linter))
    linter.register_checker(UnicodeChecker(linter))
    linter.register_checker(SyntaxChecker(linter))
