# Can I Use Python 3?

[![Build Status](https://travis-ci.org/brettcannon/caniusepython3.png?branch=master)](http://img.shields.io/travis/brettcannon/caniusepython3.svg)

You can read the documentation on how to use caniusepython3 from its
[PyPI page](https://pypi.python.org/pypi/caniusepython3).


# How do you tell if a project has been ported to Python 3?

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
end up listed on the [Python3 Packages list on PyPI](https://pypi.python.org/pypi?%3Aaction=packages_rss)).

The other way is through a [manual override](https://github.com/brettcannon/caniusepython3/blob/master/caniusepython3/overrides.json) in
`caniusepython3` itself. This list of projects exists because:

* They are now part of [Python's standard library](http://docs.python.org/3/py-modindex.html) in some release of Python 3
* Their Python 3 port is under a different name
* They are missing a Python 3 trove classifier but have actually been ported

If any of these various requirements are met, then a project is considered to
support Python 3 and thus will be added to the manual overrides list. You can
see the list of overrides when you run the script with verbose output turned on.


# How can I get a project ported to Python 3?

Typically projects which have not switched to Python 3 yet are waiting for:

* A dependency to be ported to Python 3
* Someone to volunteer to put in the time and effort to do the port

Since `caniusepython3` will tell you what dependencies are blocking a project
that you depend on from being ported, you can try to port a project farther
down your dependency graph to help a more direct dependency make the transition.

Which brings up the second point: volunteering to do a port. Most projects
happily accept help, they just have not done the port yet because they have
not had the time. Some projects are simply waiting for people to ask for it, so
even speaking up politely and requesting a port can get the process started.

If you are looking for help to port a project, you can always search online for
various sources of help. If you want a specific starting point there are
[HOWTOs](http://docs.python.org/3/howto/index.html) in the Python documentation
on [porting pure Python modules](http://docs.python.org/3/howto/pyporting.html)
and [extension modules](http://docs.python.org/3/howto/cporting.html).

# Change Log

## 2.1.0
* Verbose output will print what manual overrides are used and why
  (when available)
* Fix logging to only be configured when running as a script as well as fix a
  format bug
* Usual override updates

## 2.0.3
* Fixed `setup.py caniusepython3` to work with `extras_require` properly
* Fix various errors triggered from the moving of the `just_name()` function to
  a new module in 2.0.0 (patch by Vaibhav Sagar w/ input from Jannis Leidel)
* Usual overrides tweaks (thanks to CyrilRoelandteNovance for contributing)

## 2.0.2
* Fix lack of unicode usage in a test
* Make Python 2.6 happy again due to its distate of empty XML-RPC results

## 2.0.1
* Fix syntax error

## 2.0.0
* Tweak overrides
* `-r`, `-m`, and `-p` now take 1+ arguments instead of a single comma-separated
  list
* Unrecognized projects are considered ported to prevent the lack of info on
  the unrecognized project perpetually suggesting that it's never been ported
* Introduced `icanusepython3.check()`

## 1.2.1
* Fix `-v` to actually do something again
* Tweaked overrides

## 1.2.0
* `-r` accepts a comma-separated list of file paths

## 1.1.0
* Setuptools command support
* Various fixes

## 1.0
Initial release.
