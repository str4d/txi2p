# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.interfaces import IAddress
from twisted.python.util import FancyEqMixin
from zope.interface import implementer


@implementer(IAddress)
class I2PAddress(FancyEqMixin, object):
    """
    An L{I2PAddress} represents the address of an L{I2PEndpoint}.

    @ivar destination: An I2P Destination byte string; for example, b'example.i2p'.
    @type destination: L{bytes}

    @ivar port: (Optional) An integer representing the port number.
    @type port: L{int}
    """
    compareAttributes = ('destination', 'port')

    def __init__(self, destination, port=None):
        self.destination = destination
        self.port = int(port) if port else None


    def __repr__(self):
        if self.port:
            return '%s(%s, %d)' % (
                self.__class__.__name__, self.destination, self.port)
        return '%s(%s)' % (
            self.__class__.__name__, self.destination)


    def __hash__(self):
        return hash((self.destination, self.port))
