# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from builtins import object
from twisted.internet.endpoints import clientFromString
from twisted.internet.interfaces import IStreamClientEndpointStringParserWithReactor
from twisted.internet.interfaces import IStreamServerEndpointStringParser
from zope.interface import implementer

from txi2p.bob.endpoints import BOBI2PClientEndpoint, BOBI2PServerEndpoint
from txi2p.sam.endpoints import (
    SAMI2PStreamClientEndpoint,
    SAMI2PStreamServerEndpoint,
)
from txi2p.utils import getApi

from twisted.plugin import IPlugin


def _parseOptions(options):
    return dict([option.split(':') for option in options.split(',')]) if options else {}

@implementer(IPlugin, IStreamClientEndpointStringParserWithReactor)
class I2PClientParser(object):
    prefix = 'i2p'

    def _parseBOBClient(self, reactor, host, port, bobEndpoint,
                     tunnelNick=None,
                     inhost='localhost',
                     inport=None,
                     options=None):
        return BOBI2PClientEndpoint(reactor, clientFromString(reactor, bobEndpoint),
                                    host, port, tunnelNick, inhost,
                                    inport and int(inport) or None,
                                    _parseOptions(options))

    def _parseSAMClient(self, reactor, host, port, samEndpoint,
                     nickname=None,
                     autoClose=False,
                     keyfile=None,
                     localPort=None,
                     options=None,
                     sigType=None):
        return SAMI2PStreamClientEndpoint.new(
            clientFromString(reactor, samEndpoint),
            host, port, nickname, autoClose, keyfile,
            localPort and int(localPort) or None, _parseOptions(options), sigType)

    _apiParsers = {
        'BOB': _parseBOBClient,
        'SAM': _parseSAMClient,
        }

    def _parseClient(self, reactor, host, port=None,
                     api=None, apiEndpoint=None, **kwargs):
        api, apiEndpoint = getApi(api, apiEndpoint, self._apiParsers)
        return self._apiParsers[api](self, reactor, host,
                                     port and int(port) or None,
                                     apiEndpoint, **kwargs)

    def parseStreamClient(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseClient(reactor, *args, **kwargs)


@implementer(IPlugin, IStreamServerEndpointStringParser)
class I2PServerParser(object):
    prefix = 'i2p'

    def _parseBOBServer(self, reactor, keyfile, port, bobEndpoint,
                     tunnelNick=None,
                     outhost='localhost',
                     outport=None,
                     options=None):
        return BOBI2PServerEndpoint(reactor, clientFromString(reactor, bobEndpoint),
                                    keyfile, port, tunnelNick, outhost,
                                    outport and int(outport) or None,
                                    _parseOptions(options))

    def _parseSAMServer(self, reactor, keyfile, port, samEndpoint,
                     nickname=None,
                     autoClose=False,
                     options=None,
                     sigType=None):
        return SAMI2PStreamServerEndpoint.new(
            clientFromString(reactor, samEndpoint),
            keyfile, port, nickname, autoClose, _parseOptions(options), sigType)

    _apiParsers = {
        'BOB': _parseBOBServer,
        'SAM': _parseSAMServer,
        }

    def _parseServer(self, reactor, keyfile, port=None,
                     api=None, apiEndpoint=None, **kwargs):
        api, apiEndpoint = getApi(api, apiEndpoint, self._apiParsers)
        return self._apiParsers[api](self, reactor, keyfile,
                                     port and int(port) or None,
                                     apiEndpoint, **kwargs)

    def parseStreamServer(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseServer(reactor, *args, **kwargs)
