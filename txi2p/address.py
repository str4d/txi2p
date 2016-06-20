# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import base64
import hashlib
from twisted.internet.interfaces import IAddress, ITransport
from twisted.internet.protocol import Protocol
from twisted.python.util import FancyEqMixin
from zope.interface import implementer


@implementer(IAddress)
class I2PAddress(FancyEqMixin, object):
    """An :class:`IAddress` that represents the address of an I2P Destination.

    Args:
        destination (str): An I2P Destination string in I2P-style B64 format, or
            an :class:`I2PAddress`. In the latter case, the default host is also
            taken from the provided address.
        host (str): An I2P host string; for example, ``'example.i2p'``.
        port (int): An integer representing the port number.

    Attributes:
        destination (str): An I2P Destination string in I2P-style B64 format.
        host (str): An I2P host string; for example, ``'example.i2p'`` or
            ``'fiftytwocharacters.b32.i2p'``. If looked up, it is guaranteed to
            resolve to ``destination``.
        port (int): An integer representing the port number. Will be ``None`` if
            no port is configured.
    """
    compareAttributes = ('destination', 'port')

    def __init__(self, destination, host=None, port=None):
        if hasattr(destination, 'destination'):
            self.destination = destination.destination
        else:
            self.destination = destination
        self.port = int(port) if port else None

        if host:
            self.host = host
        elif hasattr(destination, 'host'):
            self.host = destination.host
        else:
            raw_key = base64.b64decode(destination, '-~')
            hash = hashlib.sha256(raw_key)
            base32_hash = base64.b32encode(hash.digest())
            self.host = base32_hash.lower().replace('=', '')+'.b32.i2p'


    def __repr__(self):
        if self.port:
            return '%s(%s, %d)' % (
                self.__class__.__name__, self.host, self.port)
        return '%s(%s)' % (
            self.__class__.__name__, self.host)


    def __hash__(self):
        return hash((self.host, self.port))


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


class I2PServerTunnelProtocol(Protocol):
    def __init__(self, wrappedProto, serverAddr):
        self.wrappedProto = wrappedProto
        self._serverAddr = serverAddr
        self.peer = None

    def connectionMade(self):
        # Substitute transport for an I2P wrapper
        self.transport = I2PTunnelTransport(self.transport, self._serverAddr)
        self.wrappedProto.makeConnection(self.transport)

    def dataReceived(self, data):
        if self.peer:
            # Pass all other data to the wrapped Protocol.
            self.wrappedProto.dataReceived(data)
        else:
            # First line is the peer's Destination.
            self.setPeer(data)

    def setPeer(self, data):
        self.peer = I2PAddress(data.split('\n')[0])
        self.transport.peerAddr = self.peer

    def connectionLost(self, reason):
        self.wrappedProto.connectionLost(reason)
