# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.interfaces import IAddress, ITransport
from twisted.python.util import FancyEqMixin
from zope.interface import implementer


@implementer(IAddress)
class I2PAddress(FancyEqMixin, object):
    """
    An L{I2PAddress} represents the address of an L{I2PEndpoint}.

    @ivar destination: An I2P Destination byte string.
    @type destination: L{bytes}

    @ivar host: An I2P host byte string; for example, b'example.i2p' or
    b'fiftytwocharacters.b32.i2p'. If looked up, it is guaranteed to resolve to
    destination.
    @type host: L{bytes}

    @ivar port: (Optional) An integer representing the port number.
    @type port: L{int}
    """
    compareAttributes = ('destination', 'port')

    def __init__(self, destination, host=None, port=None):
        self.destination = destination
        self.host = host
        self.port = int(port) if port else None


    def __repr__(self):
        if self.port:
            return '%s(%s, %d)' % (
                self.__class__.__name__, self.host if self.host else self.destination, self.port)
        return '%s(%s)' % (
            self.__class__.__name__, self.host if self.host else self.destination)


    def __hash__(self):
        return hash((self.destination, self.port))


@implementer(ITransport)
class I2PTunnelTransport(object):
    def __init__(self, wrappedTransport, localAddr, peerAddr=None):
        self.t = wrappedTransport
        self._localAddr = localAddr
        self.peerAddr = peerAddr

    def __getattr__(self, attr):
        return getattr(self.t, attr)

    def getPeer(self):
        return self.peerAddr

    def getHost(self):
        return self._localAddr
