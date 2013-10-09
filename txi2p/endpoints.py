# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, interfaces, protocol
from zope.interface import implementer

from txi2p.client import I2PClientFactory
from txi2p.server import I2PServerFactory


@implementer(interfaces.IStreamClientEndpoint)
class I2PClientEndpoint(object):
    """
    I2P client endpoint.
    """

    def __init__(self, dest, bobEndpoint):
        validateDestination(dest)
        self.dest = dest
        self.bobEndpoint = bobEndpoint

    def connect(self, fac):
        """
        Connect over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P client tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        i2pFac = I2PClientFactory(self.dest, fac)
        d = self.bobEndpoint.connect(i2pFac)
        d.addCallback(lambda proto: i2pFac.deferred)
        return d


@implementer(interfaces.IStreamServerEndpoint)
class I2PServerEndpoint(object):
    """
    I2P server endpoint.
    """

    # TODO: Implement properly
    def __init__(self, STUFF, bobEndpoint):
        self.STUFF = STUFF
        self.bobEndpoint = bobEndpoint

    def listen(self, fac):
        """
        Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        i2pFac = I2PServerFactory(self.STUFF, fac) # TODO: Implement properly
        d = self.bobEndpoint.connect(i2pFac)
        d.addCallback(lambda proto: i2pFac.deferred)
        return d
