Can I Use Python 3?
===================

This script takes in a set of dependencies and then figures out which
of them are holding you up from porting to Python 3.

You can specify your dependencies in multiple ways::

    python3 -m caniusepython3 -r requirements.txt
    python3 -m caniusepython3 -m PKG-INFO
    python3 -m caniusepython3 -p numpy,scipy,ipython

The output of the script will list which projects are directly holding up some
(implicit) dependency from working on Python 3.
For instance, `ecdsa <- paramiko` means that the `ecdsa` project is blocking
`paramiko` from being ported to Python 3. Any project listed without a
blocking dependency means there is no external project holding up a port and
thus the project can be ported when they have the time and manpower to do so.

<!-- END long_description -->

[![Build Status](https://travis-ci.org/brettcannon/caniusepython3.png?branch=master)](https://travis-ci.org/brettcannon/caniusepython3)


How do you tell a project has been ported to Python 3?
------------------------------------------------------
On [PyPI](https://pypi.python.org/) each project specifies various
[trove classifiers](https://pypi.python.org/pypi?%3Aaction=list_classifiers).
There are various classifiers related to what version of Python a project can
run on. E.g.:

    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.0
    Programming Language :: Python :: 3.1
    Programming Language :: Python :: 3.2
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4

As long as a trove classifier for some version of Python 3 is specified then the
project is considered to support Python 3 (project owners: it is preferred you
**at least** specify `Programming Language :: Python :: 3` as that is how you
end up on listed on the [Python3 Packages list on PyPI](https://pypi.python.org/pypi?%3Aaction=packages_rss)).

The other way is through a manual override. This project maintains a hard-coded
list of projects which are considered ported because:

* They are part of the [Python's standard library](http://docs.python.org/3/py-modindex.html) in some version of Python 3
* Their Python 3 port is under a different name
* They are missing a Python 3 trove classifier but have actually been ported

If any of these various requirements are met, then a project is considered to
support Python 3.
