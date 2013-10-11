from twisted.internet.endpoints import clientFromString
from twisted.internet.interfaces import IStreamClientEndpointStringParserWithReactor
from twisted.internet.interfaces import IStreamServerEndpointStringParser
from twisted.python.compat import _PY3
from zope.interface import implementer

from txi2p.endpoints import BOBI2PClientEndpoint, BOBI2PServerEndpoint

DEFAULT_BOB_ENDPOINT = 'tcp:127.0.0.1:2827'

if not _PY3:
    from twisted.plugin import IPlugin
else:
    from zope.interface import Interface
    class IPlugin(Interface):
        pass


@implementer(IPlugin, IStreamClientEndpointStringParserWithReactor)
class _I2PClientParser(object):
    prefix = 'i2pbob'

    def _parseClient(self, reactor, dest, bobEndpoint=DEFAULT_BOB_ENDPOINT):
        return BOBI2PClientEndpoint(reactor, clientFromString(reactor, bobEndpoint),
                                    dest)

    def parseStreamClient(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseClient(reactor, *args, **kwargs)


@implementer(IPlugin, IStreamServerEndpointStringParser)
class _I2PServerParser(object):
    prefix = 'i2pbob'

    def _parseServer(self, reactor, keypairPath, bobEndpoint=DEFAULT_BOB_ENDPOINT):
        return BOBI2PServerEndpoint(reactor, clientFromString(reactor, bobEndpoint),
                                    keypairPath)

    def parseStreamServer(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseServer(reactor, *args, **kwargs)
