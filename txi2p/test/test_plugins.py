# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from twisted.internet.endpoints import getPlugins
from twisted.python.versions import Version
from twisted.test.proto_helpers import MemoryReactor
from twisted.trial import unittest
import twisted
from zope.interface.verify import verifyObject

from txi2p.bob.endpoints import (BOBI2PClientEndpoint,
                                 BOBI2PServerEndpoint)

if twisted.version < Version('twisted', 14, 0, 0):
    skip = 'txi2p.plugins requires twisted 14.0 or newer'
else:
    skip = None


class I2PPluginTestMixin(object):
    def test_pluginDiscovery(self):
        parsers = list(getPlugins(self._parserInterface))
        for p in parsers:
            if isinstance(p, self._parserClass):
                break
        else:
            self.fail(
                "Did not find %s parser in %r" % (self._parserClass, parsers,))

    def test_interface(self):
        parser = self._parserClass()
        self.assertTrue(verifyObject(self._parserInterface, parser))


class I2PClientEndpointPluginTest(I2PPluginTestMixin, unittest.TestCase):
    """
    Unit tests for the I2P client endpoint description parser.
    """

    skip = skip
    _parserInterface = interfaces.IStreamClientEndpointStringParserWithReactor
    @property
    def _parserClass(self):
        from txi2p.plugins import I2PClientParser
        return I2PClientParser

    def test_stringDescription(self):
        from twisted.internet.endpoints import clientFromString
        ep = clientFromString(
            MemoryReactor(), "i2p:stats.i2p:api=BOB:tunnelNick=spam:inport=12345")
        self.assertIsInstance(ep, BOBI2PClientEndpoint)
        self.assertIsInstance(ep._reactor, MemoryReactor)
        self.assertEqual(ep._dest,"stats.i2p")
        self.assertEqual(ep._tunnelNick,"spam")
        self.assertEqual(ep._inport,12345)


class I2PServerEndpointPluginTest(I2PPluginTestMixin, unittest.TestCase):
    """
    Unit tests for the I2P client endpoint description parser.
    """

    skip = skip
    _parserInterface = interfaces.IStreamServerEndpointStringParser
    @property
    def _parserClass(self):
        from txi2p.plugins import I2PServerParser
        return I2PServerParser

    def test_stringDescription(self):
        from twisted.internet.endpoints import serverFromString
        ep = serverFromString(
            MemoryReactor(), "i2p:/tmp/testkeys.foo:api=BOB:tunnelNick=spam:outport=23456")
        self.assertIsInstance(ep, BOBI2PServerEndpoint)
        self.assertIsInstance(ep._reactor, MemoryReactor)
        self.assertEqual(ep._keypairPath, "/tmp/testkeys.foo")
        self.assertEqual(ep._tunnelNick, "spam")
        self.assertEqual(ep._outport, 23456)
