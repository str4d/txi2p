# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import defer, error, interfaces
from twisted.internet.endpoints import serverFromString
from zope.interface import implementer

from txi2p.sam.base import I2PFactoryWrapper
from txi2p.sam.session import SAMSession, getSession
from txi2p.sam.stream import (
    StreamConnectFactory,
    StreamAcceptPort,
    StreamForwardFactory,
    StreamForwardPort,
)


def _parseHost(host):
    # TODO: Validate I2P domain, B32 etc.
    return (host, None) if host[-4:] == '.i2p' else (None, host)

def _parseOptions(options):
    return dict([option.split(':') for option in options.split(',')]) if options else {}


@implementer(interfaces.IStreamClientEndpoint)
class SAMI2PStreamClientEndpoint(object):
    """I2P stream client endpoint backed by the SAM API.

    Args:
        session (txi2p.sam.SAMSession): The SAM session to connect with.
        host (str): The I2P hostname or Destination to connect to.
        port (int): The port to connect to inside I2P. If unset or `None`, the
            default (null) port is used. Ignored if the SAM server doesn't
            support SAM v3.2 or higher.
        localPort (int): The port to connect from inside I2P. This can be used
            to distinguish between multiple connections to the same server. If
            unset or `None`, the default (null) port is used. Ignored if the SAM
            server doesn't support SAM v3.2 or higher.
    """

    @classmethod
    def new(cls, samEndpoint, host, port=None, nickname=None, autoClose=False, keyfile=None, localPort=None, options=None):
        """Create an I2P client endpoint backed by the SAM API.

        If a SAM session for ``nickname`` already exists, it will be used, and
        all options other than ``host`` and ``port`` will be ignored. Otherwise,
        a new SAM session will be created. The implication of this is that by
        default, all endpoints (both client and server) created by the same
        process will use the same SAM session.

        Args:
            samEndpoint (twisted.internet.interfaces.IStreamClientEndpoint): An
                endpoint that will connect to the SAM API.
            host (str): The I2P hostname or Destination to connect to.
            port (int): The port to connect to inside I2P. If unset or `None`,
                the default (null) port is used. Ignored if the SAM server
                doesn't support SAM v3.2 or higher.
            nickname (str): The SAM session nickname.
            autoClose (bool): `true` if the session should close automatically
                once no more connections are using it.
            keyfile (str): Path to a local file containing the keypair to use
                for the session Destination. If non-existent, new keys will be
                generated and stored.
            localPort (int): The port to connect from inside I2P. This can be
                used to distinguish between multiple connections to the same
                server. If unset or `None`, the default (null) port is used.
                Ignored if the SAM server doesn't support SAM v3.2 or higher.
            options (dict): I2CP options to configure the session with.
        """
        d = getSession(nickname,
                       samEndpoint=samEndpoint,
                       autoClose=autoClose,
                       keyfile=keyfile,
                       options=_parseOptions(options))
        return cls(d, host, port, localPort)

    def __init__(self, session, host, port=None, localPort=None):
        self._host, self._dest = _parseHost(host)
        self._port = port
        self._localPort = localPort
        if isinstance(session, SAMSession):
            self._session = session
        else:
            self._session = None
            self._sessionDeferred = session

    def connect(self, fac):
        """Connect over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P client tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        def createStream(val):
            if self._session.style != 'STREAM':
                raise error.UnsupportedSocketType()

            i2pFac = StreamConnectFactory(fac, self._session, self._host, self._dest, self._port, self._localPort)
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
    """I2P server endpoint backed by the SAM API.

    Args:
        session (txi2p.sam.SAMSession): The SAM session to listen on.
    """

    @classmethod
    def new(cls, samEndpoint, keyfile, port=None, nickname=None, autoClose=False, options=None):
        """Create an I2P server endpoint backed by the SAM API.

        If a SAM session for ``nickname`` already exists, it will be used, and
        all options other than ``port`` will be ignored. Otherwise, a new SAM
        session will be created. The implication of this is that by default, all
        endpoints (both client and server) created by the same process will use
        the same SAM session.

        Args:
            samEndpoint (twisted.internet.interfaces.IStreamClientEndpoint): An
                endpoint that will connect to the SAM API.
            keyfile (str): Path to a local file containing the keypair to use
                for the session Destination. If non-existent, new keys will be
                generated and stored.
            port (int): The port to listen on inside I2P. If unset or `None`,
                the default (null) port is used. Ignored if the SAM server
                doesn't support SAM v3.2 or higher.
            nickname (str): The SAM session nickname.
            autoClose (bool): `true` if the session should close automatically
                once no more connections are using it.
            options (dict): I2CP options to configure the session with.
        """
        d = getSession(nickname,
                       samEndpoint=samEndpoint,
                       autoClose=autoClose,
                       keyfile=keyfile,
                       localPort=port,
                       options=_parseOptions(options))
        return cls(d)

    def __init__(self, session):
        if isinstance(session, SAMSession):
            self._session = session
        else:
            self._session = None
            self._sessionDeferred = session

    def listen(self, fac):
        """Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        def createAcceptingStream(val):
            if self._session.style != 'STREAM':
                raise error.UnsupportedSocketType()

            p = StreamAcceptPort(self._session, fac)
            p.startListening()
            return p

#        def createForwardingStream(val):
#            if self._session.style != 'STREAM':
#                raise error.UnsupportedSocketType()
#
#            serverEndpoint = serverFromString(self._reactor,
#                                              'tcp:0:interface=127.0.0.1')
#            wrappedFactory = I2PFactoryWrapper(fac, self._session.address)
#            d = serverEndpoint.listen(wrappedFactory)
#
#            def setupForward(port):
#                local_port = port.getHost().port
#                i2pFac = StreamForwardFactory(self._session, local_port)
#                d2 = self._session.samEndpoint.connect(i2pFac)
#                d2.addCallback(lambda proto: i2pFac.deferred)
#                d2.addCallback(lambda forwardingProto: (port, forwardingProto))
#                return d2
#
#            def handlePort((port, forwardingProto)):
#                return StreamForwardPort(port, forwardingProto, self._session.address)
#
#            d.addCallback(setupForward)
#            d.addCallback(handlePort)
#            return d

        if self._session:
            return createAcceptingStream(None)

        def saveSession(session):
            self._session = session
            return None
        self._sessionDeferred.addCallback(saveSession)
        self._sessionDeferred.addCallback(createAcceptingStream)
        return self._sessionDeferred
