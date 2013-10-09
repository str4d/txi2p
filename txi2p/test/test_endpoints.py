# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.trial import unittest

from txi2p.test.util import FakeEndpoint
from txi2p import endpoints


connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())



class I2PBOBEndpointsTestCase(unittest.TestCase):
    """
    Tests for I2P Endpoints backed by the BOB API.
    """

    def test_bobConnectionFailed(self):
        bobEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        endpoint = endpoints.I2PClientEndpoint('', bobEndpoint)
        d = endpoint.connect(None)
        return self.assertFailure(d, ConnectionRefusedError)


    def test_destination(self):
        bobEndpoint = FakeEndpoint()
        endpoint = endpoints.I2PClientEndpoint('foo.i2p', bobEndpoint)
        endpoint.connect(None)
        self.assertEqual(proxy.transport.value(), 'foo.i2p') # TODO: Fix.
