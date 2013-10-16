# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.bob.factory import BOBI2PClientFactory, BOBI2PServerFactory


class BOBFactoryTestMixin(object):
    def setUp(self):
        self.aborted = []

    def makeProto(self, *a, **kw):
        fac = self.factory(*a, **kw)
        proto = fac.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: self.aborted.append(True)
        proto.makeConnection(transport)
        return fac, proto

    def test_defaultFactoryListsTunnels(self):
        fac, proto = self.makeProto(object(), object(), object(), '')
        proto.dataReceived('BOB 00.00.10\nOK\n')
        self.assertEqual(proto.transport.value(), 'list\n')


class TestBOBI2PClientFactory(BOBFactoryTestMixin, unittest.TestCase):
    factory = BOBI2PClientFactory


class TestBOBI2PServerFactory(BOBFactoryTestMixin, unittest.TestCase):
    factory = BOBI2PServerFactory
