# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from twisted.internet.endpoints import serverFromString
from zope.interface import implementer

from txi2p.sam.base import I2PFactoryWrapper, I2PListeningPort
from txi2p.sam.session import getSession
from txi2p.sam.stream import StreamConnectFactory, StreamForwardFactory


def parseHost(host):
    # TODO: Validate I2P domain, B32 etc.
    return (host, None) if host[-4:] == '.i2p' else (None, host)

def parseOptions(options):
    return dict([option.split(':') for option in options.split(',')]) if options else {}


@implementer(interfaces.IStreamClientEndpoint)
class SAMI2PStreamClientEndpoint(object):
    """
    I2P stream client endpoint backed by the SAM API.
    """

    def __init__(self, samEndpoint, host,
                 port=None,
                 nickname=None,
                 options=None):
        self._samEndpoint = samEndpoint
        self._host, self._dest = parseHost(host)
        self._port = port
        self._nickname = nickname
        self._options = parseOptions(options)

    def connect(self, fac):
        """
        Connect over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P client tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        d = getSession(self._samEndpoint, self._nickname,
                       options=self._options)
        def createStream(session):
            i2pFac = StreamConnectFactory(fac, session, self._host, self._dest)
            d2 = self._samEndpoint.connect(i2pFac)
            # Once the SAM IProtocol is returned, wait for the
            # real IProtocol to be returned after tunnel creation,
            # and pass it to any further registered callbacks.
            d2.addCallback(lambda proto: i2pFac.deferred)
            return d2
        d.addCallback(createStream)
        return d


@implementer(interfaces.IStreamServerEndpoint)
class SAMI2PStreamServerEndpoint(object):
    """
    I2P server endpoint backed by the SAM API.
    """

    def __init__(self, reactor, samEndpoint, keyfile,
                 port=None,
                 nickname=None,
                 options=None):
        self._reactor = reactor
        self._samEndpoint = samEndpoint
        self._keyfile = keyfile
        self._port = port
        self._nickname = nickname
        self._options = parseOptions(options)

    def listen(self, fac):
        """
        Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        d = getSession(self._samEndpoint, self._nickname,
                       keyfile=self._keyfile, options=self._options)

        def createStream(session):
            serverEndpoint = serverFromString(self._reactor,
                                              'tcp:0:interface=127.0.0.1')
            wrappedFactory = I2PFactoryWrapper(fac, session.address)
            d2 = serverEndpoint.listen(wrappedFactory)

            def setupForward(port):
                local_port = port.getHost().port
                i2pFac = StreamForwardFactory(session, local_port)
                d3 = self._samEndpoint.connect(i2pFac)
                d3.addCallback(lambda proto: i2pFac.deferred)
                d3.addCallback(lambda forwardingProto: (port, forwardingProto))
                return d3

            def handlePort((port, forwardingProto)):
                return I2PListeningPort(port, forwardingProto, session.address)

            d2.addCallback(setupForward)
            d2.addCallback(handlePort)
            return d2

        d.addCallback(createStream)
        return d
