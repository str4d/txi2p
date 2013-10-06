from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.interfaces import IStreamClientEndpointStringParserWithReactor
from twisted.internet.interfaces import IStreamServerEndpointStringParser
from twisted.python.compat import _PY3
from zope.interface import implementer

from i2p.twisted.client import I2PClientEndpoint
from i2p.twisted.server import I2PServerEndpoint

if not _PY3:
    from twisted.plugin import IPlugin
else:
    from zope.interface import Interface
    class IPlugin(Interface):
        pass


@implementer(IPlugin, IStreamClientEndpointStringParserWithReactor)
class _I2PClientParser(object):
    prefix = 'i2p'

    # TODO: Other parameters? Define endpoint description string.
    def _parseClient(self, reactor, dest, bobHost='127.0.0.1', bobPort='2827'):
        bobPort = int(bobPort)
        bobEndpoint = TCP4ClientEndpoint(reactor, bobHost, bobPort)
        return I2PClientEndpoint(dest, bobEndpoint)

    def parseStreamClient(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseClient(reactor, *args, **kwargs)


@implementer(IPlugin, IStreamServerEndpointStringParser)
class _I2PServerParser(object):
    prefix = 'i2p'

    # TODO: Implement properly
    def _parseServer(self, reactor, STUFF, bobHost='127.0.0.1', bobPort='2827'):
        bobPort = int(bobPort)
        bobEndpoint = TCP4ClientEndpoint(reactor, bobHost, bobPort)
        return I2PServerEndpoint(STUFF, bobEndpoint)

    def parseStreamServer(self, reactor, *args, **kwargs):
        # Delegate to another function with a sane signature.  This function has
        # an insane signature to trick zope.interface into believing the
        # interface is correctly implemented.
        return self._parseServer(reactor, *args, **kwargs)
