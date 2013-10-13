# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import ClientFactory

from txi2p.bob.protocol import I2PClientTunnelCreatorBOBClient


class BOBI2PClientFactory(ClientFactory):
    protocol = I2PClientTunnelCreatorBOBClient
    bobProto = None
    canceled = False

    def _cancel(self, d):
        self.bobProto.sender.transport.abortConnection()
        self.canceled = True

    def __init__(self, reactor, clientFactory, bobEndpoint, dest):
        self._reactor = reactor
        self._clientFactory = clientFactory
        self._bobEndpoint = bobEndpoint
        self.dest = dest
        self.deferred = Deferred(self._cancel);

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        self.bobProto = proto
        return proto

    def i2pConnectionFailed(self, reason):
        if not self.canceled:
            self.deferred.errback(reason)

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.i2pConnectionFailed(reason)

    def i2pTunnelCreated(self):
        # BOB is now listening for a tunnel.
        # BOB only listens on TCP4 (for now).
        clientEndpoint = TCP4ClientEndpoint(self._reactor, self.inhost, self.inport)
        # Wrap the client Factory.
        wrappedFactory = self._clientFactory # TODO: Write wrapper
        d = clientEndpoint.connect(wrappedFactory)
        if d is None: # Shouldn't happen? Should the proto None check be a callback?
            self.deferred.cancel()
            return
        # Return the Deferred, which will return an IProtocol.
        self.deferred.callback(d)
