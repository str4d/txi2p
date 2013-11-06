# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.trial import unittest

from txi2p.bob import endpoints
from txi2p.test.util import FakeEndpoint, FakeFactory


connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())



class BOBI2PClientEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P client Endpoint backed by the BOB API.
    """

    def test_bobConnectionFailed(self):
        reactor = object()
        bobEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        endpoint = endpoints.BOBI2PClientEndpoint(reactor, bobEndpoint, '')
        d = endpoint.connect(None)
        return self.assertFailure(d, ConnectionRefusedError)


    def TODO_test_destination(self):
        reactor = object()
        bobEndpoint = FakeEndpoint()
        endpoint = endpoints.BOBI2PClientEndpoint(reactor, bobEndpoint, 'foo.i2p')
        endpoint.connect(None)
        self.assertEqual(bobEndpoint.transport.value(), 'foo.i2p') # TODO: Fix.


    def TODO_test_clientDataSent(self):
        reactor = object()
        wrappedFac = FakeFactory()
        bobEndpoint = FakeEndpoint()
        endpoint = endpoints.BOBI2PClientEndpoint(reactor, bobEndpoint, '')
        endpoint.connect(wrappedFac)
        bobEndpoint.proto.transport.clear()
        wrappedFac.proto.transport.write('xxxxx')
        self.assertEqual(bobEndpoint.proto.transport.value(), 'xxxxx')
