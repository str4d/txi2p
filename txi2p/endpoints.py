# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, interfaces, protocol
from twisted.internet.endpoints import clientFromString
from zope.interface import implementer

from txi2p.client import BOBI2PClientFactory
from txi2p.server import BOBI2PServerFactory

DEFAULT_BOB_ENDPOINT = 'tcp:127.0.0.1:2827'


def validateDestination(dest):
    # TODO: Validate I2P domain, B32 etc.
    pass


@implementer(interfaces.IStreamClientEndpoint)
class BOBI2PClientEndpoint(object):
    """
    I2P client endpoint backed by the BOB API.
    """

    def __init__(self, reactor, dest, port=None, bobEndpoint=DEFAULT_BOB_ENDPOINT):
        validateDestination(dest)
        self._reactor = reactor
        self._dest = dest
        self._port = port
        self._bobString = bobEndpoint

    def connect(self, fac):
        """
        Connect over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P client tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        bobEndpoint = clientFromString(self._reactor, self._bobString)
        i2pFac = BOBI2PClientFactory(fac, self._dest)
        d = bobEndpoint.connect(i2pFac)
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

    def __init__(self, reactor, keypairPath, bobEndpoint=DEFAULT_BOB_ENDPOINT):
        self._reactor = reactor
        self._keypairPath = keypairPath
        self._bobString = bobEndpoint

    def listen(self, fac):
        """
        Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        bobEndpoint = clientFromString(self._reactor, self._bobString)
        i2pFac = BOBI2PServerFactory(fac, self._keypairPath)
        d = bobEndpoint.connect(i2pFac)
        # Once the BOB IProtocol is returned, wait for the
        # IListeningPort to be returned after tunnel creation,
        # and pass it to any further registered callbacks.
        d.addCallback(lambda proto: i2pFac.deferred)
        return d
