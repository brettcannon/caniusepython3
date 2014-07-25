Can I Use Python 3?
===================

The goal of ``caniusepython3`` is to tell you whether your project is ready for
Python 3. This is accomplished through two methods:

1. Figuring out if all of your project's dependencies have Python 3 support
2. Providing custom Pylint_ checkers which help make sure your code is
   source-compatible with both Python 2 and 3

The idea is that you use a tool like futurize_ or modernize3k_ to make your code
compatible with both Python 2 and 3 simultaneously. Once you have, you use the
Pylint checkers to make sure you don't accidentally introduce a regression that
breaks your Python 2/3 source compatibility. See the
`Python porting HOWTO <https://docs.python.org/3/howto/pyporting.html>`__ for
details on how to port your code.

Simultaneously, you use ```caniusepython3`` to figure out which of your dependencies
are blocking you from using Python 3. This is done simultaneously instead of as
an initial blocker so that you can modernize your code to work with Python 3 to
gain various benefits -- e.g. cleaner code -- and to also make sure your own
project does not become a blocker for using Python 3 once all of your
dependencies have been ported.

Dependency compatibility checking
/////////////////////////////////

Command-line/Web usage
----------------------

You can specify your dependencies in multiple ways::

    caniusepython3 -r requirements.txt test-requirement.txt
    caniusepython3 -m PKG-INFO
    caniusepython3 -p numpy scipy ipython
    # If your project's setup.py uses setuptools
    # (note that setup_requires can't be checked) ...
    python setup.py caniusepython3

The output of the script will tell you how many (implicit) dependencies you need
to transition to Python 3 in order to allow you to make the same transition. It
will also list what projects have no dependencies blocking their
transition so you can ask them to start a port to Python 3.

If you prefer a web interface you can use https://caniusepython3.com by
Jannis Leidel.


Integrating with your tests
---------------------------

If you want to check for Python 3 availability as part of your tests, you can
use ``icanusepython3.check()``::

    def check(requirements_paths=[], metadata=[], projects=[]):
        """Return True if all of the specified dependencies have been ported to Python 3.

        The requirements_paths argument takes a sequence of file paths to
        requirements files. The 'metadata' argument takes a sequence of strings
        representing metadata. The 'projects' argument takes a sequence of project
        names.

        Any project that is not listed on PyPI will be considered ported.
        """

You can then integrate it into your tests like so::

  import unittest
  import caniusepython3

  class DependenciesOnPython3(unittest.TestCase):
    def test_dependencies(self):
      # Will begin to fail when dependencies are no longer blocking you
      # from using Python 3.
      self.assertFalse(caniusepython3.check(projects=['ipython']))

For the change log, how to tell if a project has been ported, as well as help on
how to port a project, please see the
`project website <https://github.com/brettcannon/caniusepython3>`__.

Secret, bonus feature
---------------------
If you would like to use a different name for the script and
setuptools command then set the environment variable ``CIU_ALT_NAME`` to what
you would like the alternative name to be. Reddit suggests ``icanhazpython3``.


Pylint_ checkers
////////////////
Using a `pylintrc` file with Pylint allows one to use 3rd-party checkers with
Pylint. The
`example configuration <https://github.com/brettcannon/caniusepython3/blob/master/pylintrc>`__
from ``caniusepython3`` shows how to do with along with checkers included with
Pylint which will warn you about potential regressions in your code in terms of
Python 2/3 compatibility. The checkers are somewhat aggressive on purpose as
Pylint makes it easy to turn off warnings.

The checks provided by ``caniusepython3`` are:

* Use of the ``print`` or ``exec`` statement
* ``__getslice__``, ``__setslice__``, ``__cmp__``, ``__coerce__``,
  ``__unicode__``, and ``next`` methods defined
* ``buffer``, ``apply``, ``cmp``, ``file``, ``raw_input``, ``long``, ``coerce``,
  ``execfile``, ``xrange``, ``unicode``, ``StandardError``, ``map``, ``round``,
  and ``zip`` built-ins referenced
* Non-floor division without ``from __future__ import division``
* Python 2-style octal and long literals
* Raw strings (i.e. a string literal missing a ``b``/``u`` prefix or
  ``from __future__ import unicode_literals``)
* Imports w/o ``from __future__ import absolute_import``
* Assignment to ``__metaclass__``
* Parameter unpacking

If you want to understand why these warnings/errors exist,
`Porting to Python 3 <http://python3porting.com/>`__ has a comprehensive list of
changes between Python 2 and 3.

.. _futurize: http://python-future.org/automatic_conversion.html
.. _modernize3k: https://pypi.python.org/pypi/modernize3k/
.. _Pylint: http://pylint.org/
