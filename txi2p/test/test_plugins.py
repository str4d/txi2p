# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from twisted.internet.endpoints import clientFromString, getPlugins
from twisted.python.versions import Version
from twisted.test.proto_helpers import MemoryReactor
from twisted.trial import unittest
import twisted
from zope.interface.verify import verifyObject

from txi2p.bob.endpoints import (BOBI2PClientEndpoint,
                                 BOBI2PServerEndpoint)
from txi2p.plugins import I2PClientParser

if twisted.version < Version('twisted', 14, 0, 0):
    skip = 'txi2p.plugins requires twisted 14.0 or newer'
else:
    skip = None


class I2PClientEndpointPluginTest(unittest.TestCase):
    """
    Unit tests for the I2P client endpoint description parser.
    """

    skip = skip
    _parserClass = I2PClientParser

    def test_pluginDiscovery(self):
        parsers = list(getPlugins(
            interfaces.IStreamClientEndpointStringParserWithReactor))
        for p in parsers:
            if isinstance(p, self._parserClass):
                break
        else:
            self.fail(
                "Did not find I2PClientEndpoint parser in %r" % (parsers,))

    def test_interface(self):
        parser = self._parserClass()
        self.assertTrue(verifyObject(
            interfaces.IStreamClientEndpointStringParserWithReactor, parser))

    def test_stringDescription(self):
        ep = clientFromString(
            MemoryReactor(), "i2p:stats.i2p:api=BOB:tunnelNick=spam:inport=12345")
        self.assertIsInstance(ep, BOBI2PClientEndpoint)
        self.assertIsInstance(ep._reactor, MemoryReactor)
        self.assertEqual(ep._dest,"stats.i2p")
        self.assertEqual(ep._tunnelNick,"spam")
        self.assertEqual(ep._inport,12345)
