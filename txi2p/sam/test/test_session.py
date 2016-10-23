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
from txi2p.sam import session
from txi2p.test.util import TEST_B64
from .util import SAMProtocolTestMixin, SAMFactoryTestMixin

if twisted.version < Version('twisted', 12, 3, 0):
    skipSRO = 'TestCase.successResultOf() requires twisted 12.3 or newer'
else:
    skipSRO = None


class TestSessionCreateProtocol(SAMProtocolTestMixin, unittest.TestCase):
    protocol = session.SessionCreateProtocol

    def test_sessionCreateAfterHello(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=foo DESTINATION=TRANSIENT\n',
            proto.transport.value())

    def test_sessionCreateWithAutoNickAfterHello(self):
        fac, proto = self.makeProto()
        fac.nickname = None
        fac.style = 'STREAM'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=txi2p-%s DESTINATION=TRANSIENT\n' % os.getpid(),
            proto.transport.value())

    def test_sessionCreateWithPortAfterHello(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        fac.localPort = 81
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=foo DESTINATION=TRANSIENT FROM_PORT=81\n',
            proto.transport.value())

    def test_sessionCreateWithOptionsAfterHello(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        fac.options['bar'] = 'baz'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=foo DESTINATION=TRANSIENT bar=baz\n',
            proto.transport.value())

    def test_sessionCreateReturnsError(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=I2P_ERROR MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('I2P_ERROR', 'foo bar baz')

    def test_namingLookupAfterSessionCreate(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=OK DESTINATION=%s\n' % TEST_B64)
        self.assertEquals(
            'NAMING LOOKUP NAME=ME\n',
            proto.transport.value())

    def test_sessionCreatedAfterNamingLookup(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        fac.sessionCreated = Mock()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=OK DESTINATION=%s\n' % TEST_B64)
        proto.transport.clear()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        fac.sessionCreated.assert_called()

    def test_sessionCreatedAndKeepaliveStartedAfterNamingLookupWith3_2(self):
        fac, proto = self.makeProto()
        fac.style = 'STREAM'
        fac.sessionCreated = Mock()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.2\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=OK DESTINATION=%s\n' % TEST_B64)
        proto.transport.clear()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        self.assertEquals('State_keepalive', proto.receiver.currentRule)
        fac.sessionCreated.assert_called()
        # Cleanup
        self.addCleanup(proto.receiver.stopPinging)


class FakeEndpoint(object):
    def __init__(self, failure=None):
        self.failure = failure
        self.deferred = None
        self.facDeferred = None
        self.called = 0

    def connect(self, fac):
        self.called += 1
        fac.deferred = self.facDeferred
        self.factory = fac
        return self.deferred


class TestSessionCreateFactory(SAMFactoryTestMixin, unittest.TestCase):
    factory = session.SessionCreateFactory
    blankFactoryArgs = ('',)

    def test_startFactory(self):
        tmp = '/tmp/TestSessionCreateFactory.privKey'
        fac, proto = self.makeProto('foo', keyfile=tmp)
        fac.doStart()
        self.assertTrue(fac._writeKeypair)

    def test_startFactoryWithExistingKeyfile(self):
        tmp = '/tmp/TestSessionCreateFactory.privKey'
        f = open(tmp, 'w')
        f.write('foo')
        f.close()
        fac, proto = self.makeProto('foo', keyfile=tmp)
        fac.doStart()
        self.assertEqual('foo', fac.privKey)
        os.remove(tmp)

    def test_sessionCreated(self):
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto('foo')
        fac.samVersion = '3.1'
        # Shortcut to end of SAM session create protocol
        proto.receiver.currentRule = 'State_naming'
        proto._parser._setupInterp()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        s = self.successResultOf(fac.deferred)
        self.assertEqual(('3.1', 'STREAM', 'foo', proto.receiver, TEST_B64, None), s)
    test_sessionCreated.skip = skipSRO

    def test_sessionCreatedWithKeyfile(self):
        tmp = '/tmp/TestSessionCreateFactory.privKey'
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto('foo', keyfile=tmp)
        fac.samVersion = '3.1'
        fac.privKey = 'bar'
        fac._writeKeypair = True
        # Shortcut to end of SAM session create protocol
        proto.receiver.currentRule = 'State_naming'
        proto._parser._setupInterp()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        f = open(tmp, 'r')
        privKey = f.read()
        f.close()
        self.assertEqual('bar', privKey)
        # Cleanup
        os.remove(tmp)


class TestSAMSession(unittest.TestCase):
    def setUp(self):
        self.tr = proto_helpers.StringTransportWithDisconnection()
        proto = Mock()
        proto.sender = Mock()
        proto.sender.transport = self.tr
        self.tr.protocol = proto
        self.s = session.SAMSession()
        self.s.nickname = 'foo'
        self.s.samVersion = '3.1'
        self.s.id = 'foo'
        self.s._proto = proto
        session._sessions['foo'] = self.s

    def tearDown(self):
        session._sessions = {}

    def test_addStream(self):
        self.assertEqual([], self.s._streams)
        self.s.addStream('foo')
        self.assertEqual(['foo'], self.s._streams)

    def test_removeStream_autoClose(self):
        self.s._autoClose = True
        self.s.addStream('bar')
        self.s.addStream('baz')
        self.s.removeStream('bar')
        self.assertEqual(['baz'], self.s._streams)
        self.assertEqual(True, session._sessions.has_key('foo'))
        self.assertEqual(self.s, session._sessions['foo'])
        self.s.removeStream('baz')
        self.assertEqual([], self.s._streams)
        self.assertEqual({}, session._sessions)

    def test_removeStream_noAutoClose(self):
        self.s.addStream('bar')
        self.s.addStream('baz')
        self.s.removeStream('bar')
        self.assertEqual(['baz'], self.s._streams)
        self.assertEqual(True, session._sessions.has_key('foo'))
        self.assertEqual(self.s, session._sessions['foo'])
        self.s.removeStream('baz')
        self.assertEqual([], self.s._streams)
        self.assertEqual({'foo': self.s}, session._sessions)


class TestGetSession(unittest.TestCase):
    def tearDown(self):
        session._sessions = {}

    def test_getSession_newNickname(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(('3.1', 'STREAM', 'nick', proto, TEST_B64, None))
        d = session.getSession('nick', samEndpoint)
        s = self.successResultOf(d)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual('nick', s.nickname)
        self.assertEqual('nick', s.id)
        self.assertEqual(proto, s._proto)
        self.assertEqual(TEST_B64, s.address.destination)
        self.assertEqual(None, s.address.port)
    test_getSession_newNickname.skip = skipSRO

    def test_getSession_newNickname_withPort(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(('3.2', 'STREAM', 'nick', proto, TEST_B64, 81))
        d = session.getSession('nick', samEndpoint)
        s = self.successResultOf(d)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual('nick', s.nickname)
        self.assertEqual('nick', s.id)
        self.assertEqual(proto, s._proto)
        self.assertEqual(TEST_B64, s.address.destination)
        self.assertEqual(81, s.address.port)
    test_getSession_newNickname_withPort.skip = skipSRO

    def test_getSession_newNickname_withoutEndpoint(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(('3.1', 'STREAM', 'nick', proto, TEST_B64, None))
        self.assertRaises(ValueError, session.getSession, 'nick')
    test_getSession_newNickname_withoutEndpoint.skip = skipSRO

    def test_getSession_existingNickname(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(('3.1', 'STREAM', 'nick', proto, TEST_B64, None))
        d = session.getSession('nick', samEndpoint)
        s = self.successResultOf(d)
        d2 = session.getSession('nick', samEndpoint)
        s2 = self.successResultOf(d2)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual(s, s2)
    test_getSession_existingNickname.skip = skipSRO

    def test_getSession_existingNickname_withoutEndpoint(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(('3.1', 'STREAM', 'nick', proto, TEST_B64, None))
        d = session.getSession('nick', samEndpoint)
        s = self.successResultOf(d)
        d2 = session.getSession('nick')
        s2 = self.successResultOf(d2)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual(s, s2)
    test_getSession_existingNickname_withoutEndpoint.skip = skipSRO


class TestDestGenerateProtocol(SAMProtocolTestMixin, unittest.TestCase):
    protocol = session.DestGenerateProtocol

    def test_destGenerateAfterHello(self):
        fac, proto = self.makeProto()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals('DEST GENERATE\n', proto.transport.value())

    def test_destGenerated(self):
        fac, proto = self.makeProto()
        fac.destGenerated = Mock()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('DEST REPLY PUB=%s PRIV=%s\n' % (TEST_B64, 'TEST_PRIV'))
        fac.destGenerated.assert_called_with(TEST_B64, 'TEST_PRIV')


class TestDestGenerateFactory(SAMFactoryTestMixin, unittest.TestCase):
    factory = session.DestGenerateFactory
    blankFactoryArgs = ('',)

    def test_destGenerated(self):
        tmp = '/tmp/TestDestGenerateFactory.privKey'
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto(tmp)
        # Shortcut to end of SAM dest generate protocol
        proto.receiver.currentRule = 'State_dest'
        proto._parser._setupInterp()
        proto.dataReceived('DEST REPLY PUB=%s PRIV=%s\n' % (TEST_B64, 'TEST_PRIV'))
        s = self.successResultOf(fac.deferred)
        self.assertEqual(I2PAddress(TEST_B64), s)
        os.remove(tmp)
    test_destGenerated.skip = skipSRO

    def test_destGenerated_privKeySaved(self):
        tmp = '/tmp/TestDestGenerateFactory.privKey'
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto(tmp)
        # Shortcut to end of SAM dest generate protocol
        proto.receiver.currentRule = 'State_dest'
        proto._parser._setupInterp()
        proto.dataReceived('DEST REPLY PUB=%s PRIV=%s\n' % (TEST_B64, 'TEST_PRIV'))
        f = open(tmp, 'r')
        privKey = f.read()
        f.close()
        self.assertEqual('TEST_PRIV', privKey)
        os.remove(tmp)

    def test_destGenerated_keyfileExists(self):
        tmp = '/tmp/TestDestGenerateFactory.privKey'
        f = open(tmp, 'w')
        f.write('foo')
        f.close()
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto(tmp)
        # Shortcut to end of SAM dest generate protocol
        proto.receiver.currentRule = 'State_dest'
        proto._parser._setupInterp()
        proto.dataReceived('DEST REPLY PUB=%s PRIV=%s\n' % (TEST_B64, 'TEST_PRIV'))
        self.assertIsInstance(self.failureResultOf(fac.deferred).value, ValueError)
        os.remove(tmp)
    test_destGenerated_keyfileExists.skip = skipSRO


class TestGenerateDestination(unittest.TestCase):
    def test_generateDestination(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(I2PAddress(TEST_B64))
        d = session.generateDestination('', samEndpoint)
        s = self.successResultOf(d)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual(I2PAddress(TEST_B64), s)
    test_generateDestination.skip = skipSRO


class TestTestAPIProtocol(SAMProtocolTestMixin, unittest.TestCase):
    protocol = session.TestAPIProtocol

    def test_samConnected(self):
        fac, proto = self.makeProto()
        fac.samConnected = Mock()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        fac.samConnected.assert_called_with()


class TestTestAPIFactory(SAMFactoryTestMixin, unittest.TestCase):
    factory = session.TestAPIFactory
    blankFactoryArgs = []

    def test_samConnected(self):
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        s = self.successResultOf(fac.deferred)
        self.assertEqual(True, s)
    test_samConnected.skip = skipSRO


class TestTestAPI(unittest.TestCase):
    def test_testAPI(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(True)
        d = session.testAPI(samEndpoint)
        s = self.successResultOf(d)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual(True, s)
    test_testAPI.skip = skipSRO
