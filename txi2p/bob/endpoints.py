# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from zope.interface import implementer

from txi2p.bob.factory import BOBI2PClientFactory, BOBI2PServerFactory


def _validateDestination(dest):
    # TODO: Validate I2P domain, B32 etc.
    pass


@implementer(interfaces.IStreamClientEndpoint)
class BOBI2PClientEndpoint(object):
    """I2P client endpoint backed by the BOB API.

    Args:
        reactor: The client endpoint will be constructed with this reactor.
        bobEndpoint (twisted.internet.interfaces.IStreamClientEndpoint): An
            endpoint that will connect to the BOB API.
        host (str): The I2P hostname or Destination to connect to.
        port (int): The port to connect to inside I2P. If unset or `None`, the
            default (null) port is used. Ignored because BOB doesn't support
            ports yet.
        tunnelNick (str): The tunnel nickname to use. If a tunnel with this
            nickname already exists, it will be used. The default is ``txi2p-#``
            where ``#`` is the PID of the current process.

            * The implication of this is that by default, all endpoints (both
              client and server) created by the same process will use the same
              BOB tunnel.

        inhost (str): The host that the tunnel created by BOB will listen on.
            Defaults to ``localhost``.
        inport (int): The port that the tunnel created by BOB will listen on.
            Defaults to a port over 9000.
        options (dict): I2CP options to configure the tunnel with.
    """

    def __init__(self, reactor, bobEndpoint, dest,
                 port=None,
                 tunnelNick=None,
                 inhost='localhost',
                 inport=None,
                 options=None):
        _validateDestination(dest)
        self._reactor = reactor
        self._bobEndpoint = bobEndpoint
        self._dest = dest
        self._port = port
        self._tunnelNick = tunnelNick
        self._inhost = inhost
        self._inport = inport
        self._options = options

    def connect(self, fac):
        """Connect over I2P.

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
    """I2P server endpoint backed by the BOB API.

    Args:
        reactor: The server endpoint will be constructed with this reactor.
        bobEndpoint (twisted.internet.interfaces.IStreamClientEndpoint): An
            endpoint that will connect to the BOB API.
        keyfile (str): Path to a local file containing the keypair to use for
            the server Destination. If non-existent, new keys will be generated
            and stored.
        port (int): The port to connect to inside I2P. If unset or `None`, the
            default (null) port is used. Ignored because BOB doesn't support
            ports yet.
        tunnelNick (str): The tunnel nickname to use. If a tunnel with this
            nickname already exists, it will be used. The default is ``txi2p-#``
            where ``#`` is the PID of the current process.

            * The implication of this is that by default, all endpoints (both
              client and server) created by the same process will use the same
              BOB tunnel.

        outhost (str): The host that the tunnel created by BOB will forward data
            to. Defaults to ``localhost``.
        outport (int): The port that the tunnel created by BOB will forward data
            to. Defaults to a port over 9000.
        options (dict): I2CP options to configure the tunnel with.
    """

    def __init__(self, reactor, bobEndpoint, keyfile,
                 port=None,
                 tunnelNick=None,
                 outhost='localhost',
                 outport=None,
                 options=None):
        self._reactor = reactor
        self._bobEndpoint = bobEndpoint
        self._keyfile = keyfile
        self._port = port
        self._tunnelNick = tunnelNick
        self._outhost = outhost
        self._outport = outport
        self._options = options

    def listen(self, fac):
        """Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        i2pFac = BOBI2PServerFactory(self._reactor, fac, self._bobEndpoint, self._keyfile,
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
