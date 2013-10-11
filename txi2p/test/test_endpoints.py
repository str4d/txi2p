# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.trial import unittest

from txi2p.test.util import FakeEndpoint
from txi2p import endpoints


connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())



class BOBI2PClientEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P client Endpoint backed by the BOB API.
    """

    def test_bobConnectionFailed(self):
        bobEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        endpoint = endpoints.BOBI2PClientEndpoint(bobEndpoint, '')
        d = endpoint.connect(None)
        return self.assertFailure(d, ConnectionRefusedError)


    def test_destination(self):
        bobEndpoint = FakeEndpoint()
        endpoint = endpoints.BOBI2PClientEndpoint(bobEndpoint, 'foo.i2p')
        endpoint.connect(None)
        self.assertEqual(bobEndpoint.transport.value(), 'foo.i2p') # TODO: Fix.


    def test_clientDataSent(self):
        wrappedFac = FakeFactory()
        bobEndpoint = FakeEndpoint()
        endpoint = endpoints.BOBI2PClientEndpoint(bobEndpoint, '')
        endpoint.connect(wrappedFac)
        bobEndpoint.proto.transport.clear()
        wrappedFac.proto.transport.write('xxxxx')
        self.assertEqual(bobEndpoint.proto.transport.value(), 'xxxxx')
