# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer
from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.test import proto_helpers

connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())


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
