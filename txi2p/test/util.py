# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, protocol
from twisted.test import proto_helpers

TEST_B64 = "2wDRF5nDfeTNgM4X-TI5xEk3R-WiaTABvkMQ2eYpvEzayUZQJgr9E2T6Y2m9HHn3xHYGEOg-RLisjW9AubTaUTx-v66AsEEtv745qPcuWuV1SP~w1bdzYEn8MSoK7Zh4mwHBg1uHq8z17TUNvWz19q76vHNth-2PDuBToD7ySBn3cGBFDUU83wJJXPD6OueLY8yosWWtksk7WZk60~6z~nVePPSEY8JDry3myLDe11szAVER4A8eX1sFpw247cXGGJK9wQhV-TXFj~m76GPVcFKh7u79zwTwZnZ1GXXKqqyRoj1c4-U69CvvJsQRLmdLFwFEpRkxwV8z6LIFclYJk443YpTnPXC7vNdFOzqqS4FLR1ra~DNfN5foMtR2~2VxuR5m2dYiOS6GzHDxA4acJJSGqnasJjcEIFNVSQKxMnFu9PvGLNJHZ83EraHCErENcOGkPlnVgcJCtPGNGiirwCbBz38jE0lfjkrNrWabc6uWeU559CobG8F8KUDx1irpAAAA"
TEST_B32 = "tv5iv4i5roywnv2rg6rjqufniqbogn4rokjkooa7n4jht3lex3ga.b32.i2p"


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
