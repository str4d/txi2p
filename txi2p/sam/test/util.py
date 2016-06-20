# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from mock import Mock
from twisted.internet import defer
from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.internet.protocol import ClientFactory
from twisted.python import failure
from twisted.test import proto_helpers

from txi2p.sam import constants as c

connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())


class SAMProtocolTestMixin(object):
    def makeProto(self, *a, **kw):
        protoClass = kw.pop('_protoClass', self.protocol)
        fac = ClientFactory(*a, **kw)
        fac.nickname = 'foo'
        fac.privKey = None
        fac.port = None
        fac.localPort = None
        fac.options = {}
        fac.protocol = protoClass
        fac.resultNotOK = Mock()
        def raise_(ex):
            raise ex
        fac.connectionFailed = lambda reason: raise_(reason)
        proto = fac.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: None
        proto.makeConnection(transport)
        return fac, proto

    def test_initSendsHello(self):
        fac, proto = self.makeProto()
        self.assertSubstring('HELLO VERSION', proto.transport.value())

    def test_helloReturnsError(self):
        fac, proto = self.makeProto()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=I2P_ERROR MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('I2P_ERROR', 'foo bar baz')

    def test_pingReceived(self):
        fac, proto = self.makeProto()
        self.addCleanup(proto.receiver.stopPinging)
        proto.transport.clear()
        # Enable keepalive
        proto.receiver.currentRule = 'State_keepalive'
        proto._parser._setupInterp()
        proto.dataReceived('PING\n')
        self.assertEquals(
            'PONG\n',
            proto.transport.value())

    def test_pingReceivedWithData(self):
        fac, proto = self.makeProto()
        self.addCleanup(proto.receiver.stopPinging)
        proto.transport.clear()
        # Enable keepalive
        proto.receiver.currentRule = 'State_keepalive'
        proto._parser._setupInterp()
        proto.dataReceived('PING some random data\n')
        self.assertEquals(
            'PONG some random data\n',
            proto.transport.value())

    def test_pingReceivedResetsTimeout(self):
        fac, proto = self.makeProto()
        self.addCleanup(proto.receiver.stopPinging)
        proto.transport.clear()
        # Enable keepalive
        proto.receiver.currentRule = 'State_keepalive'
        proto._parser._setupInterp()
        proto.receiver._sendPing()
        self.assertEquals(
            'PING %s\n' % proto.receiver.lastPing,
            proto.transport.value())
        self.assertTrue(proto.receiver.pingTimeout.active())
        proto.transport.clear()
        proto.dataReceived('PING\n')
        self.assertEquals(
            'PONG\n',
            proto.transport.value())
        self.assertFalse(proto.receiver.pingTimeout.active())

    def test_validPongResponseResetsTimeout(self):
        fac, proto = self.makeProto()
        self.addCleanup(proto.receiver.stopPinging)
        proto.transport.clear()
        # Enable keepalive
        proto.receiver.currentRule = 'State_keepalive'
        proto._parser._setupInterp()
        proto.receiver._sendPing()
        self.assertEquals(
            'PING %s\n' % proto.receiver.lastPing,
            proto.transport.value())
        self.assertTrue(proto.receiver.pingTimeout.active())
        proto.transport.clear()
        proto.dataReceived('PONG %s\n' % proto.receiver.lastPing)
        self.assertFalse(proto.receiver.pingTimeout.active())

    def test_invalidPongResponseDoesNotResetTimeout(self):
        fac, proto = self.makeProto()
        self.addCleanup(proto.receiver.stopPinging)
        proto.transport.clear()
        # Enable keepalive
        proto.receiver.currentRule = 'State_keepalive'
        proto._parser._setupInterp()
        proto.receiver._sendPing()
        self.assertEquals(
            'PING %s\n' % proto.receiver.lastPing,
            proto.transport.value())
        self.assertTrue(proto.receiver.pingTimeout.active())
        proto.transport.clear()
        proto.dataReceived('PONG not what was expected\n')
        self.assertTrue(proto.receiver.pingTimeout.active())


class SAMFactoryTestMixin(object):
    def setUp(self):
        self.aborted = []

    def makeProto(self, *a, **kw):
        fac = self.factory(*a, **kw)
        proto = fac.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: self.aborted.append(True)
        proto.makeConnection(transport)
        return fac, proto

    def test_cancellation(self):
        fac, proto = self.makeProto(*self.blankFactoryArgs)
        fac.deferred.cancel()
        self.assert_(self.aborted)
        return self.assertFailure(fac.deferred, defer.CancelledError)

    def test_cancellationBeforeFailure(self):
        fac, proto = self.makeProto(*self.blankFactoryArgs)
        fac.deferred.cancel()
        proto.connectionLost(connectionLostFailure)
        self.assert_(self.aborted)
        return self.assertFailure(fac.deferred, defer.CancelledError)

    def test_cancellationAfterFailure(self):
        fac, proto = self.makeProto(*self.blankFactoryArgs)
        proto.connectionLost(connectionLostFailure)
        fac.deferred.cancel()
        self.assertFalse(self.aborted)
        return self.assertFailure(fac.deferred, ConnectionLost)

    def test_clientConnectionFailed(self):
        fac, proto = self.makeProto(*self.blankFactoryArgs)
        fac.clientConnectionFailed(None, connectionRefusedFailure)
        return self.assertFailure(fac.deferred, ConnectionRefusedError)

    def test_resultNotOK(self):
        fac, proto = self.makeProto(*self.blankFactoryArgs)
        for result, error in c.samErrorMap.items():
            self.assertRaises(error, fac.resultNotOK, result, '')
