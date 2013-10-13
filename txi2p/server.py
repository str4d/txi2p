# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory

from txi2p.bob.protocol import I2PServerTunnelCreatorBOBClient


class BOBI2PServerFactory(Factory):
    protocol = I2PServerTunnelCreatorBOBClient
    bobProto = None
    canceled = False

    def _cancel(self, d):
        self.bobProto.sender.transport.abortConnection()
        self.canceled = True

    def __init__(self, reactor, serverFactory, bobEndpoint, keypairPath):
        self._reactor = reactor
        self._serverFactory = serverFactory
        self._bobEndpoint = bobEndpoint
        self.keypairPath = keypairPath
        self.deferred = Deferred(self._cancel)

    def startFactory(self):
        try:
            keypairFile = open(self.keypairPath, 'r')
            self.keypair = keypairFile.read()
            keypairFile.close()
        except IOError:
            self.keypair = None

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        self.bobProto = proto
        return proto

    def i2pTunnelCreated(self):
        # BOB will now forward data to a listener.
        # BOB only forwards to TCP4 (for now).
        serverEndpoint = TCP4ServerEndpoint(self._reactor, self.outport)
        # Wrap the server Factory.
        wrappedFactory = self._serverFactory # TODO: Write wrapper
        d = serverEndpoint.connect(wrappedFactory)
        if d is None: # Shouldn't happen? Should the proto None check be a callback?
            self.deferred.cancel()
            return
        # Return the Deferred, which will return an IListeningPort.
        self.deferred.callback(d)
