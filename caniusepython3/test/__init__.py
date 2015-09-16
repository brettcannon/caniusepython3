try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest import mock
except ImportError:
    import mock

try:
    from xmlrpc.client import Fault
except ImportError:
    from xmlrpclib import Fault

import functools

def skip_pypi_timeouts(method):
    @functools.wraps(method)
    def closure(*args, **kwargs):
        try:
            method(*args, **kwargs)
        except Fault as exc:
            if exc.faultCode == 1:
                raise unittest.SkipTest('PyPI timed out')
            raise
    return closure
