# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from mock import Mock
import os
import twisted
from twisted.internet import defer
from twisted.python.versions import Version
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.address import I2PAddress
from txi2p.sam import stream
from txi2p.test.util import TEST_B64, FakeFactory
from .util import SAMProtocolTestMixin, SAMFactoryTestMixin

if twisted.version < Version('twisted', 12, 3, 0):
    skipSRO = 'TestCase.successResultOf() requires twisted 12.3 or newer'
else:
    skipSRO = None


class TestStreamConnectProtocol(SAMProtocolTestMixin, unittest.TestCase):
    protocol = stream.StreamConnectProtocol

    def test_streamConnectAfterHello(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.dest = 'bar'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'STREAM CONNECT ID=foo DESTINATION=bar SILENT=false\n',
            proto.transport.value())

    def test_streamConnectWithPortAfterHello(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.dest = 'bar'
        fac.port = 80
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'STREAM CONNECT ID=foo DESTINATION=bar SILENT=false TO_PORT=80\n',
            proto.transport.value())

    def test_streamConnectWithLocalPortAfterHello(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.dest = 'bar'
        fac.localPort = 34444
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'STREAM CONNECT ID=foo DESTINATION=bar SILENT=false FROM_PORT=34444\n',
            proto.transport.value())

    def test_namingLookupAfterHello(self):
        fac, proto = self.makeProto()
        fac.dest = None
        fac.host = 'spam.i2p'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'NAMING LOOKUP NAME=spam.i2p\n',
            proto.transport.value())

    def test_namingLookupReturnsError(self):
        fac, proto = self.makeProto()
        fac.dest = None
        fac.host = 'spam.i2p'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('NAMING REPLY RESULT=KEY_NOT_FOUND NAME=spam.i2p MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('KEY_NOT_FOUND', 'foo bar baz')

    def test_streamConnectAfterNamingLookup(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.dest = None
        fac.host = 'spam.i2p'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=spam.i2p VALUE=bar\n')
        self.assertEquals(
            'STREAM CONNECT ID=foo DESTINATION=bar SILENT=false\n',
            proto.transport.value())

    def test_streamConnectReturnsError(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.dest = 'bar'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('STREAM STATUS RESULT=I2P_ERROR MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('I2P_ERROR', 'foo bar baz')

    def test_streamConnectionEstablishedAfterStreamConnect(self):
        fac, proto = self.makeProto()
        fac.streamConnectionEstablished = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.dest = 'bar'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('STREAM STATUS RESULT=OK\n')
        fac.streamConnectionEstablished.assert_called_with(proto.receiver)


class TestStreamConnectFactory(SAMFactoryTestMixin, unittest.TestCase):
    factory = stream.StreamConnectFactory
    blankFactoryArgs = (None, Mock(), '', '')

    def test_streamConnectionEstablished(self):
        mreactor = proto_helpers.MemoryReactor()
        wrappedFactory = FakeFactory()
        session = Mock()
        fac, proto = self.makeProto(wrappedFactory, session, 'spam.i2p', 'foo')
        # Shortcut to end of SAM stream connect protocol
        proto.receiver.currentRule = 'State_connect'
        proto._parser._setupInterp()
        proto.dataReceived('STREAM STATUS RESULT=OK\n')
        session.addStream.assert_called_with(proto.receiver)
        streamProto = self.successResultOf(fac.deferred)
        self.assertEqual(proto.receiver.wrappedProto, streamProto)
    test_streamConnectionEstablished.skip = skipSRO


class TestStreamAcceptProtocol(SAMProtocolTestMixin, unittest.TestCase):
    protocol = stream.StreamAcceptProtocol

    def test_streamAcceptAfterHello(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'STREAM ACCEPT ID=foo SILENT=false\n',
            proto.transport.value())

    def test_streamAcceptReturnsError(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('STREAM STATUS RESULT=I2P_ERROR MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('I2P_ERROR', 'foo bar baz')

    def test_streamAcceptEstablishedAfterStreamAccept(self):
        fac, proto = self.makeProto()
        fac.streamAcceptEstablished = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('STREAM STATUS RESULT=OK\n')
        fac.streamAcceptEstablished.assert_called_with(proto.receiver)

    def test_streamAcceptIncomingAfterPeerAddress(self):
        fac, proto = self.makeProto()
        fac.streamAcceptIncoming = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        # Shortcut to end of SAM stream accept protocol
        proto.receiver.currentRule = 'State_readData'
        proto._parser._setupInterp()
        proto.dataReceived('%s FROM_PORT=34444 TO_PORT=0\n' % TEST_B64)
        fac.streamAcceptIncoming.assert_called_with(proto.receiver)
        self.assertEquals(
            I2PAddress(TEST_B64, port=34444),
            proto.receiver.peer)

    def test_peerDataWrapped_allAtOnce(self):
        fac, proto = self.makeProto()
        fac.streamAcceptIncoming = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.receiver.wrappedProto = proto_helpers.AccumulatingProtocol()
        # Shortcut to end of SAM stream accept protocol
        proto.receiver.currentRule = 'State_readData'
        proto._parser._setupInterp()
        proto.dataReceived('%s FROM_PORT=34444 TO_PORT=0\nEgg and spam' % TEST_B64)
        self.assertEquals('Egg and spam', proto.receiver.wrappedProto.data)

    def test_peerDataWrapped_twoParts(self):
        fac, proto = self.makeProto()
        fac.streamAcceptIncoming = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.receiver.wrappedProto = proto_helpers.AccumulatingProtocol()
        # Shortcut to end of SAM stream accept protocol
        proto.receiver.currentRule = 'State_readData'
        proto._parser._setupInterp()
        proto.dataReceived('%s FROM_PORT=34444 TO_PORT=0\nEgg a' % TEST_B64)
        self.assertEquals('Egg a', proto.receiver.wrappedProto.data)
        proto.dataReceived('nd spam')
        self.assertEquals('Egg and spam', proto.receiver.wrappedProto.data)

    def test_peerDataWrapped_threeParts(self):
        fac, proto = self.makeProto()
        fac.streamAcceptIncoming = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.receiver.wrappedProto = proto_helpers.AccumulatingProtocol()
        # Shortcut to end of SAM stream accept protocol
        proto.receiver.currentRule = 'State_readData'
        proto._parser._setupInterp()
        proto.dataReceived('%s FROM_PORT=34444 T' % TEST_B64)
        proto.dataReceived('O_PORT=0\nEgg a')
        self.assertEquals('Egg a', proto.receiver.wrappedProto.data)
        proto.dataReceived('nd spam')
        self.assertEquals('Egg and spam', proto.receiver.wrappedProto.data)


class TestStreamAcceptFactory(SAMFactoryTestMixin, unittest.TestCase):
    factory = stream.StreamAcceptFactory
    blankFactoryArgs = (Mock(), Mock(), Mock())

    def test_streamAcceptEstablished(self):
        mreactor = proto_helpers.MemoryReactor()
        session = Mock()
        listeningPort = Mock()
        fac, proto = self.makeProto(Mock(), session, listeningPort)
        # Shortcut to end of SAM stream accept protocol
        proto.receiver.currentRule = 'State_accept'
        proto._parser._setupInterp()
        proto.dataReceived('STREAM STATUS RESULT=OK\n')
        session.addStream.assert_called_with(proto.receiver)
        listeningPort.addAccept.assert_called_with(proto.receiver)
    test_streamAcceptEstablished.skip = skipSRO

    def test_streamAcceptIncoming(self):
        mreactor = proto_helpers.MemoryReactor()
        wrappedFactory = FakeFactory()
        session = Mock()
        listeningPort = Mock()
        fac, proto = self.makeProto(wrappedFactory, session, listeningPort)
        # Shortcut to end of SAM stream accept protocol
        proto.receiver.currentRule = 'State_readData'
        proto._parser._setupInterp()
        proto.dataReceived('%s FROM_PORT=34444 TO_PORT=0\n' % TEST_B64)
        listeningPort.removeAccept.assert_called_with(proto.receiver)
        self.assertEqual(wrappedFactory.proto, proto.receiver.wrappedProto)
    test_streamAcceptEstablished.skip = skipSRO


class TestStreamForwardProtocol(SAMProtocolTestMixin, unittest.TestCase):
    protocol = stream.StreamForwardProtocol

    def test_streamForwardAfterHello(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'STREAM FORWARD ID=foo PORT=1337 SILENT=false\n',
            proto.transport.value())

    def test_streamForwardReturnsError(self):
        fac, proto = self.makeProto()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('STREAM STATUS RESULT=I2P_ERROR MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('I2P_ERROR', 'foo bar baz')

    def test_streamForwardEstablishedAfterStreamForward(self):
        fac, proto = self.makeProto()
        fac.streamForwardEstablished = Mock()
        fac.session = Mock()
        fac.session.id = 'foo'
        fac.forwardPort = 1337
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('STREAM STATUS RESULT=OK\n')
        fac.streamForwardEstablished.assert_called_with(proto.receiver)


class TestStreamForwardFactory(SAMFactoryTestMixin, unittest.TestCase):
    factory = stream.StreamForwardFactory
    blankFactoryArgs = (Mock(), '')

    def test_streamForwardEstablished(self):
        mreactor = proto_helpers.MemoryReactor()
        session = Mock()
        fac, proto = self.makeProto(session, '')
        # Shortcut to end of SAM stream forward protocol
        proto.receiver.currentRule = 'State_forward'
        proto._parser._setupInterp()
        proto.dataReceived('STREAM STATUS RESULT=OK\n')
        session.addStream.assert_called_with(proto.receiver)
        streamProto = self.successResultOf(fac.deferred)
        self.assertEqual(proto.receiver, streamProto)
    test_streamForwardEstablished.skip = skipSRO
