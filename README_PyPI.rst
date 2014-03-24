Can I Use Python 3?
===================

This script takes in a set of dependencies and then figures out which
of them are holding you up from porting to Python 3.

Command-line/Web Usage
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


Integrating With Your Tests
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
