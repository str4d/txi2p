# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.endpoints import clientFromString
from twisted.internet.interfaces import IStreamClientEndpointStringParserWithReactor
from twisted.internet.interfaces import IStreamServerEndpointStringParser
from twisted.python.compat import _PY3
from zope.interface import implementer

from txi2p.bob.endpoints import BOBI2PClientEndpoint, BOBI2PServerEndpoint

DEFAULT_ENDPOINT = {
    'BOB': 'tcp:127.0.0.1:2827',
    }

DEFAULT_API = 'BOB'

if not _PY3:
    from twisted.plugin import IPlugin
else:
    from zope.interface import Interface
    class IPlugin(Interface):
        pass


@implementer(IPlugin, IStreamClientEndpointStringParserWithReactor)
class I2PClientParser(object):
    prefix = 'i2p'

    def _parseBOBClient(self, reactor, dest, bobEndpoint,
                     tunnelNick=None,
                     inhost='localhost',
                     inport=None,
                     options=None):
        return BOBI2PClientEndpoint(reactor, clientFromString(reactor, bobEndpoint),
                                    dest, tunnelNick, inhost, inport, options)

    _apiParsers = {
        'BOB': _parseBOBClient,
        }

    def _parseClient(self, reactor, dest,
                     api=None, apiEndpoint=None, **kwargs):
        if not api:
            if apiEndpoint:
                raise ValueError('api must be specified if apiEndpoint is given')
            else:
                api = DEFAULT_API

        if not apiEndpoint:
            apiEndpoint = DEFAULT_ENDPOINT[api]

        if api not in self._apiParsers:
            raise ValueError('Specified I2P API is invalid or unsupported')
        else:
            return self._apiParsers[api](self, reactor, dest, apiEndpoint, **kwargs)

    def parseStreamClient(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseClient(reactor, *args, **kwargs)


@implementer(IPlugin, IStreamServerEndpointStringParser)
class I2PServerParser(object):
    prefix = 'i2p'

    def _parseBOBServer(self, reactor, keypairPath, bobEndpoint,
                     tunnelNick=None,
                     outhost='localhost',
                     outport=None,
                     options=None):
        return BOBI2PServerEndpoint(reactor, clientFromString(reactor, bobEndpoint),
                                    keypairPath, tunnelNick, outhost, outport, options)

    _apiParsers = {
        'BOB': _parseBOBServer,
        }

    def _parseServer(self, reactor, keypairPath,
                     api=None, apiEndpoint=None, **kwargs):
        if not api:
            if apiEndpoint:
                raise ValueError('api must be specified if apiEndpoint is given')
            else:
                api = DEFAULT_API

        if not apiEndpoint:
            apiEndpoint = DEFAULT_ENDPOINT[api]

        if api not in self._apiParsers:
            raise ValueError('Specified I2P API is invalid or unsupported')
        else:
            return self._apiParsers[api](self, reactor, keypairPath, apiEndpoint, **kwargs)

    def parseStreamServer(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseServer(reactor, *args, **kwargs)
