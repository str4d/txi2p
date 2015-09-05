# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from zope.interface import implementer

from txi2p.sam.session import getSession
from txi2p.sam.stream import StreamConnectFactory


def parseHost(host):
    # TODO: Validate I2P domain, B32 etc.
    return (host, None) if host[-4:] == '.i2p' else (None, host)

def parseOptions(options):
    return dict([option.split(':') for option in options.split(',')]) if options else {}

def killReactor(reason):
    print 'Something failed!'
    print reason
    from twisted.internet import reactor
    reactor.stop()


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
            d2.addErrback(killReactor)
            return d2
        d.addCallback(createStream)
        return d
