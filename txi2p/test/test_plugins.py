# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from twisted.python.versions import Version
from twisted.test.proto_helpers import MemoryReactor
from twisted.trial import unittest
import twisted
from zope.interface.verify import verifyObject

from txi2p.bob.endpoints import (BOBI2PClientEndpoint,
                                 BOBI2PServerEndpoint)
from txi2p.sam.endpoints import (SAMI2PStreamClientEndpoint,
                                 SAMI2PStreamServerEndpoint)

if twisted.version < Version('twisted', 14, 0, 0):
    skip = 'txi2p.plugins requires twisted 14.0 or newer'
else:
    skip = None


class I2PPluginTestMixin(object):
    def test_pluginDiscovery(self):
        from twisted.internet.endpoints import getPlugins
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
    @property
    def _parserInterface(self):
        return interfaces.IStreamClientEndpointStringParserWithReactor
    @property
    def _parserClass(self):
        from txi2p.plugins import I2PClientParser
        return I2PClientParser

    def test_badAPI(self):
        from twisted.internet.endpoints import clientFromString
        self.failUnlessRaises(ValueError, clientFromString,
            MemoryReactor(), "i2p:stats.i2p:api=FOO")

    def test_apiEndpointWithNoAPI(self):
        from twisted.internet.endpoints import clientFromString
        self.failUnlessRaises(ValueError, clientFromString,
            MemoryReactor(), "i2p:stats.i2p:apiEndpoint=tcp\:127.0.0.1\:2827")

    def test_stringDescription_default(self):
        from twisted.internet.endpoints import clientFromString
        ep = clientFromString(
            MemoryReactor(), "i2p:stats.i2p")
        self.assertIsInstance(ep, SAMI2PStreamClientEndpoint)

    def test_stringDescription_BOB(self):
        from twisted.internet.endpoints import clientFromString
        ep = clientFromString(
            MemoryReactor(), "i2p:stats.i2p:api=BOB:tunnelNick=spam:inport=12345")
        self.assertIsInstance(ep, BOBI2PClientEndpoint)
        self.assertIsInstance(ep._reactor, MemoryReactor)
        self.assertEqual(ep._dest,"stats.i2p")
        self.assertEqual(ep._tunnelNick,"spam")
        self.assertEqual(ep._inport,12345)

    def test_stringDescription_SAM(self):
        from twisted.internet.endpoints import clientFromString
        ep = clientFromString(
            MemoryReactor(), "i2p:stats.i2p:81:api=SAM:localPort=34444")
        self.assertIsInstance(ep, SAMI2PStreamClientEndpoint)
        self.assertEqual(ep._host, "stats.i2p")
        self.assertEqual(ep._port, 81)
        self.assertEqual(ep._localPort, 34444)


class I2PServerEndpointPluginTest(I2PPluginTestMixin, unittest.TestCase):
    """
    Unit tests for the I2P client endpoint description parser.
    """

    skip = skip
    @property
    def _parserInterface(self):
        return interfaces.IStreamServerEndpointStringParser
    @property
    def _parserClass(self):
        from txi2p.plugins import I2PServerParser
        return I2PServerParser

    def test_badAPI(self):
        from twisted.internet.endpoints import serverFromString
        self.failUnlessRaises(ValueError, serverFromString,
            MemoryReactor(), "i2p:/tmp/testkeys.foo:api=FOO")

    def test_apiEndpointWithNoAPI(self):
        from twisted.internet.endpoints import serverFromString
        self.failUnlessRaises(ValueError, serverFromString,
            MemoryReactor(), "i2p:/tmp/testkeys.foo:apiEndpoint=tcp\:127.0.0.1\:2827")

    def test_stringDescription_default(self):
        from twisted.internet.endpoints import serverFromString
        ep = serverFromString(
            MemoryReactor(), "i2p:/tmp/testkeys.foo")
        self.assertIsInstance(ep, SAMI2PStreamServerEndpoint)

    def test_stringDescription_BOB(self):
        from twisted.internet.endpoints import serverFromString
        ep = serverFromString(
            MemoryReactor(), "i2p:/tmp/testkeys.foo:api=BOB:tunnelNick=spam:outport=23456")
        self.assertIsInstance(ep, BOBI2PServerEndpoint)
        self.assertIsInstance(ep._reactor, MemoryReactor)
        self.assertEqual(ep._keyfile, "/tmp/testkeys.foo")
        self.assertEqual(ep._tunnelNick, "spam")
        self.assertEqual(ep._outport, 23456)

    def test_stringDescription_SAM(self):
        from twisted.internet.endpoints import serverFromString
        ep = serverFromString(
            MemoryReactor(), "i2p:/tmp/testkeys.foo:81:api=SAM")
        self.assertIsInstance(ep, SAMI2PStreamServerEndpoint)
