# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from mock import Mock
import os
import twisted
from twisted.internet import defer
from twisted.python.versions import Version
from twisted.test import proto_helpers
from twisted.trial import unittest

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
