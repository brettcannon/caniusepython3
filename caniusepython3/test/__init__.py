try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest import mock
except ImportError:
    import mock

try:
    import xmlrpc.client as xmlrpc_client
except ImportError:
    import xmlrpclib as xmlrpc_client

import functools

def skip_pypi_timeouts(method):
    @functools.wraps(method)
    def closure(*args, **kwargs):
        try:
            method(*args, **kwargs)
        except xmlrpc_client.ProtocolError as exc:
            if exc.errcode >= 500:
                raise unittest.SkipTest('PyPI had an error (probably timed out)')
            else:
                raise
        except xmlrpc_client.Fault as exc:
            if exc.faultCode == 1:
                raise unittest.SkipTest('PyPI had an error (probably timed out)')
            else:
                raise
    return closure
