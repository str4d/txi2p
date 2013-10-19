# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from zope.interface import implementer

from txi2p.bob.factory import BOBI2PClientFactory, BOBI2PServerFactory


def validateDestination(dest):
    # TODO: Validate I2P domain, B32 etc.
    pass


@implementer(interfaces.IStreamClientEndpoint)
class BOBI2PClientEndpoint(object):
    """
    I2P client endpoint backed by the BOB API.
    """

    def __init__(self, reactor, bobEndpoint, dest,
                 tunnelNick=None,
                 inhost='localhost',
                 inport=None,
                 options=None):
        validateDestination(dest)
        self._reactor = reactor
        self._bobEndpoint = bobEndpoint
        self._dest = dest
        self._tunnelNick = tunnelNick
        self._inhost = inhost
        self._inport = inport
        self._options = options

    def connect(self, fac):
        """
        Connect over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P client tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        i2pFac = BOBI2PClientFactory(self._reactor, fac, self._bobEndpoint, self._dest,
                                     self._tunnelNick,
                                     self._inhost,
                                     self._inport,
                                     self._options)
        d = self._bobEndpoint.connect(i2pFac)
        # Once the BOB IProtocol is returned, wait for the
        # real IProtocol to be returned after tunnel creation,
        # and pass it to any further registered callbacks.
        d.addCallback(lambda proto: i2pFac.deferred)
        return d


@implementer(interfaces.IStreamServerEndpoint)
class BOBI2PServerEndpoint(object):
    """
    I2P server endpoint backed by the BOB API.
    """

    def __init__(self, reactor, bobEndpoint, keypairPath,
                 tunnelNick=None,
                 outhost='localhost',
                 outport=None,
                 options=None):
        self._reactor = reactor
        self._bobEndpoint = bobEndpoint
        self._keypairPath = keypairPath
        self._tunnelNick = tunnelNick
        self._outhost = outhost
        self._outport = outport
        self._options = options

    def listen(self, fac):
        """
        Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        i2pFac = BOBI2PServerFactory(self._reactor, fac, self._bobEndpoint, self._keypairPath,
                                     self._tunnelNick,
                                     self._outhost,
                                     self._outport,
                                     self._options)
        d = self._bobEndpoint.connect(i2pFac)
        # Once the BOB IProtocol is returned, wait for the
        # IListeningPort to be returned after tunnel creation,
        # and pass it to any further registered callbacks.
        d.addCallback(lambda proto: i2pFac.deferred)
        return d
