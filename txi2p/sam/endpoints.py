# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, interfaces
from twisted.internet.endpoints import serverFromString
from zope.interface import implementer

from txi2p.sam.base import I2PFactoryWrapper, I2PListeningPort
from txi2p.sam.session import SAMSession, getSession
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

    @classmethod
    def new(cls, samEndpoint, host, port=None, nickname=None, options=None):
        d = getSession(samEndpoint, nickname, options=parseOptions(options))
        return cls(d, host, port)

    def __init__(self, session, host, port=None):
        self._host, self._dest = parseHost(host)
        self._port = port
        if isinstance(session, SAMSession):
            self._session = session
        else:
            self._session = None
            self._sessionDeferred = session

    def connect(self, fac):
        """
        Connect over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P client tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        def createStream(val):
            i2pFac = StreamConnectFactory(fac, self._session, self._host, self._dest)
            d = self._session.samEndpoint.connect(i2pFac)
            # Once the SAM IProtocol is returned, wait for the
            # real IProtocol to be returned after tunnel creation,
            # and pass it to any further registered callbacks.
            d.addCallback(lambda proto: i2pFac.deferred)
            return d

        if self._session:
            return createStream(None)

        def saveSession(session):
            self._session = session
            return None
        self._sessionDeferred.addCallback(saveSession)
        self._sessionDeferred.addCallback(createStream)
        return self._sessionDeferred


@implementer(interfaces.IStreamServerEndpoint)
class SAMI2PStreamServerEndpoint(object):
    """
    I2P server endpoint backed by the SAM API.
    """

    @classmethod
    def new(cls, reactor, samEndpoint, keyfile, port=None, nickname=None, options=None):
        d = getSession(samEndpoint, nickname, keyfile=keyfile, options=parseOptions(options))
        return cls(reactor, d, port)

    def __init__(self, reactor, session, port=None):
        self._reactor = reactor
        self._port = port
        if isinstance(session, SAMSession):
            self._session = session
        else:
            self._session = None
            self._sessionDeferred = session

    def listen(self, fac):
        """
        Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        def createStream(val):
            serverEndpoint = serverFromString(self._reactor,
                                              'tcp:0:interface=127.0.0.1')
            wrappedFactory = I2PFactoryWrapper(fac, self._session.address)
            d = serverEndpoint.listen(wrappedFactory)

            def setupForward(port):
                local_port = port.getHost().port
                i2pFac = StreamForwardFactory(self._session, local_port)
                d2 = self._session.samEndpoint.connect(i2pFac)
                d2.addCallback(lambda proto: i2pFac.deferred)
                d2.addCallback(lambda forwardingProto: (port, forwardingProto))
                return d2

            def handlePort((port, forwardingProto)):
                return I2PListeningPort(port, forwardingProto, self._session.address)

            d.addCallback(setupForward)
            d.addCallback(handlePort)
            return d

        if self._session:
            return createStream(None)

        def saveSession(session):
            self._session = session
            return None
        self._sessionDeferred.addCallback(saveSession)
        self._sessionDeferred.addCallback(createStream)
        return self._sessionDeferred
