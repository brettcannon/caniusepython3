import requests

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import functools

def skip_pypi_timeouts(method):
    @functools.wraps(method)
    def closure(*args, **kwargs):
        try:
            method(*args, **kwargs)
        except requests.ConnectionError as exc:
            raise unittest.SkipTest('PyPI had an error:' + str(exc))
    return closure
