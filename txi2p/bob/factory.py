# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet.protocol import ClientFactory, Factory

from txi2p.address import I2PAddress
from txi2p.bob.protocol import (I2PClientTunnelCreatorBOBClient,
                                I2PServerTunnelCreatorBOBClient,
                                I2PTunnelRemoverBOBClient,
                                I2PClientTunnelProtocol,
                                I2PServerTunnelProtocol,
                                I2PListeningPort)


class BOBI2PClientFactory(ClientFactory):
    protocol = I2PClientTunnelCreatorBOBClient
    bobProto = None
    canceled = False
    removeTunnelWhenFinished = True

    def _cancel(self, d):
        self.bobProto.sender.transport.abortConnection()
        self.canceled = True

    def __init__(self, reactor, clientFactory, bobEndpoint, dest,
                 tunnelNick=None,
                 inhost='localhost',
                 inport=None,
                 options=None):
        self._reactor = reactor
        self._clientFactory = clientFactory
        self._bobEndpoint = bobEndpoint
        self.dest = dest
        self.tunnelNick = tunnelNick
        self.inhost = inhost
        self.inport = inport
        self.options = options
        self.deferred = Deferred(self._cancel);

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        self.bobProto = proto
        return proto

    def bobConnectionFailed(self, reason):
        if not self.canceled:
            self.deferred.errback(reason)

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.bobConnectionFailed(reason)

    def i2pTunnelCreated(self):
        # BOB is now listening for a tunnel.
        # BOB only listens on TCP4 (for now).
        clientEndpoint = TCP4ClientEndpoint(self._reactor, self.inhost, self.inport)
        # Wrap the client Factory.
        wrappedFactory = BOBClientFactoryWrapper(self._clientFactory,
                                                 self._bobEndpoint,
                                                 I2PAddress(self.localDest),
                                                 self.tunnelNick,
                                                 self.removeTunnelWhenFinished)
        wrappedFactory.setDest(self.dest)
        d = clientEndpoint.connect(wrappedFactory)
        def checkProto(proto):
            if proto is None:
                self.deferred.cancel()
            return proto
        d.addCallback(checkProto)
        # When the Deferred returns an IProtocol, pass it on.
        d.chainDeferred(self.deferred)


class BOBI2PServerFactory(Factory):
    protocol = I2PServerTunnelCreatorBOBClient
    bobProto = None
    canceled = False
    removeTunnelWhenFinished = True

    def _cancel(self, d):
        self.bobProto.sender.transport.abortConnection()
        self.canceled = True

    def __init__(self, reactor, serverFactory, bobEndpoint, keyfile,
                 tunnelNick=None,
                 outhost='localhost',
                 outport=None,
                 options=None):
        self._reactor = reactor
        self._serverFactory = serverFactory
        self._bobEndpoint = bobEndpoint
        self._keyfile = keyfile
        self._writeKeypair = False
        self.tunnelNick = tunnelNick
        self.outhost = outhost
        self.outport = outport
        self.options = options
        self.deferred = Deferred(self._cancel)

    def startFactory(self):
        try:
            f = open(self._keyfile, 'r')
            self.keypair = f.read()
            f.close()
        except IOError:
            self.keypair = None
            self._writeKeypair = True

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        self.bobProto = proto
        return proto

    def bobConnectionFailed(self, reason):
        if not self.canceled:
            self.deferred.errback(reason)

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.bobConnectionFailed(reason)

    def i2pTunnelCreated(self):
        if self._writeKeypair:
            try:
                f = open(self._keyfile, 'w')
                f.write(self.keypair)
                f.close()
            except IOError:
                print 'Could not save keypair'
        # BOB will now forward data to a listener.
        # BOB only forwards to TCP4 (for now).
        serverEndpoint = TCP4ServerEndpoint(self._reactor, self.outport)
        # Wrap the server Factory.
        wrappedFactory = BOBServerFactoryWrapper(self._serverFactory,
                                                 self._bobEndpoint,
                                                 I2PAddress(self.localDest),
                                                 self.tunnelNick,
                                                 self.removeTunnelWhenFinished)
        d = serverEndpoint.listen(wrappedFactory)
        def handlePort(port):
            if port is None:
                self.deferred.cancel()
            serverAddr = I2PAddress(self.localDest)
            p = I2PListeningPort(port, wrappedFactory, serverAddr)
            return p
        d.addCallback(handlePort)
        # When the Deferred returns an IListeningPort, pass it on.
        d.chainDeferred(self.deferred)


class BOBFactoryWrapperCommon(object):
    def __init__(self, wrappedFactory,
                       bobEndpoint,
                       localAddr,
                       tunnelNick,
                       removeTunnelWhenFinished):
        self.w = wrappedFactory
        self.bobEndpoint = bobEndpoint
        self.localAddr = localAddr
        self.tunnelNick = tunnelNick
        self.removeTunnelWhenFinished = removeTunnelWhenFinished

    def __getattr__(self, attr):
        return getattr(self.w, attr)


class BOBClientFactoryWrapper(BOBFactoryWrapperCommon):
    protocol = I2PClientTunnelProtocol

    def setDest(self, dest):
        self.dest = dest

    def buildProtocol(self, addr):
        wrappedProto = self.w.buildProtocol(addr)
        proto = self.protocol(wrappedProto, self.localAddr, self.dest)
        proto.factory = self
        return proto

    def i2pConnectionLost(self, wrappedProto, reason):
        if self.removeTunnelWhenFinished:
            # Notify the underlying Protocol once the tunnel has
            # been removed, in case they stop the reactor.
            rmTunnelFac = BOBI2PClientTunnelRemoverFactory(self.tunnelNick,
                                                           wrappedProto,
                                                           reason)
            self.bobEndpoint.connect(rmTunnelFac)
        else:
            # Notify the underlying Protocol now.
            wrappedProto.connectionLost(reason)


class BOBServerFactoryWrapper(BOBFactoryWrapperCommon):
    protocol = I2PServerTunnelProtocol

    def buildProtocol(self, addr):
        wrappedProto = self.w.buildProtocol(addr)
        proto = self.protocol(wrappedProto, self.localAddr)
        proto.factory = self
        return proto

    def stopListening(self, wrappedPort):
        if self.removeTunnelWhenFinished:
            # Notify the underlying ListeningPort once the tunnel
            # has been removed, in case they stop the reactor.
            rmTunnelFac = BOBI2PServerTunnelRemoverFactory(self.tunnelNick,
                                                           wrappedPort)
            self.bobEndpoint.connect(rmTunnelFac)
        else:
            # Notify the underlying ListeningPort now.
            wrappedPort.stopListening()


class BOBI2PClientTunnelRemoverFactory(ClientFactory):
    protocol = I2PTunnelRemoverBOBClient

    def __init__(self, tunnelNick, protoToNotify, reason):
        self.tunnelNick = tunnelNick
        self._protoToNotify = protoToNotify
        self._reason = reason

    def i2pTunnelRemoved(self):
        # Now that the I2P tunnel has been removed,
        # notify the underlying Protocol.
        self._protoToNotify.connectionLost(self._reason)


class BOBI2PServerTunnelRemoverFactory(ClientFactory):
    protocol = I2PTunnelRemoverBOBClient

    def __init__(self, tunnelNick, portToNotify):
        self.tunnelNick = tunnelNick
        self._portToNotify = portToNotify

    def i2pTunnelRemoved(self):
        # Now that the I2P tunnel has been removed,
        # notify the underlying ListeningPort.
        self._portToNotify.stopListening()
