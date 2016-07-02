# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.sam import endpoints
from txi2p.sam.session import SAMSession
from txi2p.test.util import FakeEndpoint, FakeFactory


connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())



class SAMI2PStreamClientEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P client Endpoint backed by the SAM API.
    """

    def test_samConnectionFailed(self):
        samEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        endpoint = endpoints.SAMI2PStreamClientEndpoint.new(samEndpoint, '')
        d = endpoint.connect(None)
        return self.assertFailure(d, ConnectionRefusedError)


    def test_streamConnect(self):
        samEndpoint = FakeEndpoint()
        session = SAMSession()
        session.nickname = 'foo'
        session.samEndpoint = samEndpoint
        session.samVersion = '3.1'
        session.id = 'foo'
        session._autoClose = True
        endpoint = endpoints.SAMI2PStreamClientEndpoint(session, 'foo.i2p')
        endpoint.connect(None)
        self.assertSubstring('HELLO VERSION', samEndpoint.transport.value())



class SAMI2PStreamServerEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P server Endpoint backed by the SAM API.
    """

    def test_samConnectionFailed(self):
        samEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        endpoint = endpoints.SAMI2PStreamServerEndpoint.new(samEndpoint, '')
        d = endpoint.listen(None)
        return self.assertFailure(d, ConnectionRefusedError)


    def test_streamListen(self):
        samEndpoint = FakeEndpoint()
        session = SAMSession()
        session.nickname = 'foo'
        session.samEndpoint = samEndpoint
        session.samVersion = '3.1'
        session.id = 'foo'
        session._autoClose = True
        endpoint = endpoints.SAMI2PStreamServerEndpoint(session)
        endpoint.listen(None)
        self.assertSubstring('HELLO VERSION', samEndpoint.transport.value())
