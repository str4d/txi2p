# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

try:
    # Python 3
    from unittest import mock
except:
    # Python 2 (library)
    import mock
from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.sam import endpoints
from txi2p.sam.session import SAMSession
from txi2p.test.util import FakeEndpoint, FakeFactory, fakeSession


connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())



class SAMI2PStreamClientEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P client Endpoint backed by the SAM API.
    """

    def test_newWithOptions(self):
        samEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        with mock.patch('txi2p.sam.endpoints.getSession', fakeSession):
            endpoint = endpoints.SAMI2PStreamClientEndpoint.new(
                samEndpoint, '',
                options={'inbound.length': 5, 'outbound.length': 5})
        self.assertEqual(endpoint._sessionDeferred.kwargs['options'],
                         {'inbound.length': 5, 'outbound.length': 5})


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
        self.assertSubstring('HELLO VERSION', samEndpoint.transport.value().decode('utf-8'))



class SAMI2PStreamServerEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P server Endpoint backed by the SAM API.
    """

    def test_newWithOptions(self):
        samEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        with mock.patch('txi2p.sam.endpoints.getSession', fakeSession):
            endpoint = endpoints.SAMI2PStreamServerEndpoint.new(
                samEndpoint, '',
                options={'inbound.length': 5, 'outbound.length': 5})
        self.assertEqual(endpoint._sessionDeferred.kwargs['options'],
                         {'inbound.length': 5, 'outbound.length': 5})


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
        self.assertSubstring('HELLO VERSION', str(samEndpoint.transport.value()))
