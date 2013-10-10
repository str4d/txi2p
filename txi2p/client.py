# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, interfaces, protocol
from zope.interface import implementer


class I2PClientFactory(protocol.ClientFactory):
    currentCandidate = None
    canceled = False

    def _cancel(self, d):
        self.currentCandidate.sender.transport.abortConnection()
        self.canceled = True

    def __init__(self, dest, providedFactory):
        self.dest = dest
        self.providedFactory = providedFactory
        self.deferred = defer.Deferred(self._cancel);

    def buildProtocol(self, addr):
        proto = None # TODO: Make protocol!
        proto.factory = self
        self.currentCandidate = proto
        return proto

    def i2pConnectionFailed(self, reason):
        if not self.canceled:
            self.deferred.errback(reason)

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.i2pConnectionFailed(reason)

    def i2pConnectionEstablished(self, i2pProtocol):
        # We have a connection! Use it.
        proto = self.providedFactory.buildProtocol(
            i2pProtocol.sender.transport.getPeer()) # TODO: Understand this - need to use the new tunnel, not BOB.
        if proto is None:
            self.deferred.cancel()
            return
        i2pProtocol.i2pEstablished(proto)
        self.deferred.callback(proto)
