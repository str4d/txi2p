# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, protocol
from twisted.test import proto_helpers


class FakeFactory(protocol.ClientFactory):
    protocol = proto_helpers.AccumulatingProtocol

    def __init__(self, returnNoProtocol=False):
        self.returnNoProtocol = returnNoProtocol
        self.protocolConnectionMade = defer.Deferred()

    def buildProtocol(self, addr):
        if self.returnNoProtocol:
            return None
        self.proto = protocol.ClientFactory.buildProtocol(self, addr)
        return self.proto


class FakeEndpoint(object):
    def __init__(self, failure=None):
        self.failure = failure
        self.deferred = None

    def connect(self, fac):
        self.factory = fac
        if self.deferred:
            return self.deferred
        if self.failure:
            return defer.fail(self.failure)
        self.proto = fac.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        self.aborted = []
        transport.abortConnection = lambda: self.aborted.append(True)
        self.tlsStarts = []
        transport.startTLS = lambda ctx: self.tlsStarts.append(ctx)
        self.proto.makeConnection(transport)
        self.transport = transport
        return defer.succeed(self.proto)
