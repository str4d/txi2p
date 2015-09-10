# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from mock import Mock
import os
import twisted
from twisted.internet import defer
from twisted.python.versions import Version
from twisted.test import proto_helpers
from twisted.trial import unittest

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
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=foo DESTINATION=TRANSIENT\n',
            proto.transport.value())

    def test_sessionCreateWithAutoNickAfterHello(self):
        fac, proto = self.makeProto()
        fac.nickname = None
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=txi2p-%s DESTINATION=TRANSIENT\n' % os.getpid(),
            proto.transport.value())

    def test_sessionCreateWithOptionsAfterHello(self):
        fac, proto = self.makeProto()
        fac.options['bar'] = 'baz'
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        self.assertEquals(
            'SESSION CREATE STYLE=STREAM ID=foo DESTINATION=TRANSIENT bar=baz\n',
            proto.transport.value())

    def test_sessionCreateReturnsError(self):
        fac, proto = self.makeProto()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=I2P_ERROR MESSAGE="foo bar baz"\n')
        fac.resultNotOK.assert_called_with('I2P_ERROR', 'foo bar baz')

    def test_namingLookupAfterSessionCreate(self):
        fac, proto = self.makeProto()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=OK DESTINATION=%s\n' % TEST_B64)
        self.assertEquals(
            'NAMING LOOKUP NAME=ME\n',
            proto.transport.value())

    def test_sessionCreatedAfterNamingLookup(self):
        fac, proto = self.makeProto()
        fac.sessionCreated = Mock()
        proto.transport.clear()
        proto.dataReceived('HELLO REPLY RESULT=OK VERSION=3.1\n')
        proto.transport.clear()
        proto.dataReceived('SESSION STATUS RESULT=OK DESTINATION=%s\n' % TEST_B64)
        proto.transport.clear()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        fac.sessionCreated.assert_called()


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
        # Shortcut to end of SAM session create protocol
        proto.receiver.currentRule = 'State_naming'
        proto._parser._setupInterp()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        s = self.successResultOf(fac.deferred)
        self.assertEqual(('foo', proto.receiver, TEST_B64), s)
    test_sessionCreated.skip = skipSRO

    def test_sessionCreatedWithKeyfile(self):
        tmp = '/tmp/TestSessionCreateFactory.privKey'
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto('foo', keyfile=tmp)
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
        os.remove(tmp)


class TestSAMSession(unittest.TestCase):
    def setUp(self):
        self.tr = proto_helpers.StringTransportWithDisconnection()
        proto = Mock()
        proto.sender = Mock()
        proto.sender.transport = self.tr
        self.tr.protocol = proto
        self.s = session.SAMSession(None, 'foo', 'foo', proto, True)
        session._sessions['foo'] = self.s

    def tearDown(self):
        session._sessions = {}

    def test_addStream(self):
        self.assertEqual([], self.s._streams)
        self.s.addStream('foo')
        self.assertEqual(['foo'], self.s._streams)

    def test_removeStream_autoClose(self):
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
        self.s._autoClose = False
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
        samEndpoint.facDeferred = defer.succeed(('nick', proto, TEST_B64))
        d = session.getSession(samEndpoint, 'nick')
        s = self.successResultOf(d)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual('nick', s.nickname)
        self.assertEqual('nick', s.id)
        self.assertEqual(proto, s.proto)
        self.assertEqual(TEST_B64, s.address.destination)
    test_getSession_newNickname.skip = skipSRO

    def test_getSession_existingNickname(self):
        proto = proto_helpers.AccumulatingProtocol()
        samEndpoint = FakeEndpoint()
        samEndpoint.deferred = defer.succeed(None)
        samEndpoint.facDeferred = defer.succeed(('nick', proto, TEST_B64))
        d = session.getSession(samEndpoint, 'nick')
        s = self.successResultOf(d)
        d2 = session.getSession(samEndpoint, 'nick')
        s2 = self.successResultOf(d2)
        self.assertEqual(1, samEndpoint.called)
        self.assertEqual(s, s2)
    test_getSession_existingNickname.skip = skipSRO
