Can I Use Python 3?
===================

This script takes in a set of dependencies and then figures out which
of them are holding you up from porting to Python 3.

You can specify your dependencies in multiple ways::

    caniusepython3 -r requirements.txt test-requirement.txt
    caniusepython3 -m PKG-INFO
    caniusepython3 -p numpy scipy ipython
    # If your project's setup.py uses setuptools ...
    python setup.py caniusepython3

The output of the script will tell you how many (implicit) dependencies you need
to transition to Python 3 in order to allow you to make the same transition. It
will also list what projects have no explicit dependency blocking their
transition so you can ask them consider starting a port to Python 3.

If you prefer a web interface you can use https://caniusepython3.com by
Jannis Leidel.

For the change log, how to tell if a project has been ported, as well as help on
how to port a project, please see the
`project website <https://github.com/brettcannon/caniusepython3>`__.

Secret, bonus feature
---------------------
If you would like to use a different name for the either the script or
setuptools command, then change the `command_name` line in `setup.py`.
Reddit suggests `icanhazpython3` as an alternative.
