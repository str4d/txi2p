# Copyriht (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.sam import session
from txi2p.test.util import TEST_B64
from .util import SAMFactoryTestMixin


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

    def test_sessionCreated(self):
        mreactor = proto_helpers.MemoryReactor()
        fac, proto = self.makeProto('foo')
        # Shortcut to end of SAM session create protocol
        proto.receiver.currentRule = 'State_naming'
        proto._parser._setupInterp()
        proto.dataReceived('NAMING REPLY RESULT=OK NAME=ME VALUE=%s\n' % TEST_B64)
        s = self.successResultOf(fac.deferred)
        self.assertEqual(('foo', proto, TEST_B64), s)


class TestSAMSession(unittest.TestCase):
    def setUp(self):
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.s = session.SAMSession()
        self.s.nickname = 'foo'

    def test_addStream(self):
        self.assertEqual([], self.s.streams)
        self.s.addStream('foo')
        self.assertEqual(['foo'], self.s.streams)

    def test_removeStream(self):
        session._sessions['foo'] = self.s
        self.s.addStream('bar')
        self.s.addStream('baz')
        self.s.removeStream('bar')
        self.assertEqual(['baz'], self.s.streams)
        self.assertEqual(True, session._sessions.haskey('foo'))
        self.assertEqual(self.s, session._sessions['foo'])
        self.s.removeStream('baz')
        self.assertEqual([], self.s.streams)
        self.assertEqual({}, session._sessions)


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
