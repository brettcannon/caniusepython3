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
"""Pylint checker to enforce Python 2/3 compatible syntax.

See the documentation for what checkers pylint includes by default
which compliment this file.
"""
from __future__ import absolute_import, print_function

import token
import tokenize

from pylint import checkers, interfaces


class StrictPython3Checker(checkers.BaseChecker):

    __implements__ = interfaces.IAstroidChecker

    name = 'python3'
    msgs = {
        # Errors for what will syntactically break in Python 3, warnings for
        # everything else.
        # Retired:
        #   'W6001': 'filter built-in referenced'
        #   'W6002': 'map built-in referenced'
        #   'W6003': 'range built-in referenced'
        #   'W6004': 'zip built-in referenced'
        'W6005': ('open built-in referenced',
                  'open-builtin',
                  'Used when the open built-in function is referenced '
                  '(semantics different in Python 3; '
                  'use `from io import open`)',
                {'maxversion': (3, 0)}),
    }

    _changed_builtins = frozenset(['open'])

    def visit_name(self, node):
        if hasattr(node, 'name') and getattr(node.lookup(node.name)[0], 'name', '') == '__builtin__':
            if node.name in self._changed_builtins:
                self.add_message(node.name + '-builtin', node=node)


class UnicodeChecker(checkers.BaseTokenChecker):

    __implements__ = interfaces.ITokenChecker

    name = 'python3'
    msgs = {
        'W6100': ('native string literal',
                  'native-string',
                  'Used when a string has no `b`/`u` prefix and '
                  '`from __future__ import unicode_literals` is not found '
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
            if type_ > token.NEWLINE and type_ < token.N_TOKENS:
                module_start = False
            elif type_ == token.STRING:
                line_num += val.count('\n')
                if not module_start and not val.startswith(('u', 'b')):
                    self.add_message('native-string', line=line_num)
            elif module_start and type_ == token.NAME:
                if len(line) >= 39:  # Fast-fail check
                    if u'__future__' in line and u'unicode_literals' in line:
                        return


def register(linter):
    linter.register_checker(StrictPython3Checker(linter))
    linter.register_checker(UnicodeChecker(linter))
