"""This module contains an example of everything the custom checker looks
for.

When run through Pylint using the included pylintrc in the project you should
see a warning for nearly every line.
"""
# pylint: disable=locally-disabled,no-init,too-few-public-methods
# pylint: disable=locally-disabled,pointless-statement,unreachable
# pylint: disable=locally-disabled,pointless-string-statement,multiple-statements
# pylint: disable=locally-disabled,missing-docstring,invalid-name
import os  # pylint: disable=locally-disabled,unused-import
print u'hello, world'
exec u'2 + 3'  # pylint: disable=locally-disabled,exec-used
raise "a string"  # pylint: disable=locally-disabled,native-string
raise Exception, u"old syntax"
try: pass
except ZeroDivisionError, (a, b): pass
NO_INDEXING_EXCEPTIONS = Exception(1)[0]
u"old comparison" <> u"only for FLUFL"
`u"backticks"`
class Bad:
    __metaclass__ = type
    def __getslice__(self, i, j): pass
    def __setslice__(self, i, j, value): pass
    def __cmp__(self, other): pass
    def __coerce__(self, other): pass
    def __unicode__(self): pass
    def next(self): pass
buffer
apply
cmp
file
raw_input
long
coerce
execfile
xrange
unicode
StandardError
map(None, [1, 2, 3])
zip([1, 2, 3], [4, 5, 6])
'no prefix or future statement'
012
123L
3 / 2
def parameter_unpacking(a, (b, c)): pass  # pylint: disable=locally-disabled,redefined-outer-name,unused-argument
round(1.5)
