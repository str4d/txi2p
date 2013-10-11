# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory

from txi2p.protocol import I2PClientTunnelCreatorBOBClient


class BOBI2PClientFactory(ClientFactory):
    protocol = I2PClientTunnelCreatorBOBClient
    bobProto = None
    canceled = False

    def _cancel(self, d):
        self.bobProto.sender.transport.abortConnection()
        self.canceled = True

    def __init__(self, clientFactory, dest, port, bobString):
        self.clientFactory = clientFactory
        self.dest = dest
        self.port = port
        self.bobString = bobString
        self.deferred = Deferred(self._cancel);

    def buildProtocol(self, addr):
        proto = protocol()
        proto.factory = self
        self.bobProto = proto
        return proto

    def i2pConnectionFailed(self, reason):
        if not self.canceled:
            self.deferred.errback(reason)

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.i2pConnectionFailed(reason)

    def i2pConnectionEstablished(self, i2pProtocol):
        # We have a connection! Use it.
        proto = self.clientFactory.buildProtocol(
            i2pProtocol.sender.transport.getPeer()) # TODO: Understand this - need to use the new tunnel, not BOB.
        if proto is None:
            self.deferred.cancel()
            return
        i2pProtocol.i2pEstablished(proto)
        self.deferred.callback(proto)
