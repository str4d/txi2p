# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.protocol import ClientFactory
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.protocol import (I2PClientTunnelCreatorBOBClient,
                            I2PServerTunnelCreatorBOBClient,
                            I2PTunnelRemoverBOBClient)


class ProtoTestMixin(object):
    def makeProto(self, *a, **kw):
        protoClass = kw.pop('_protoClass', self.protocol)
        fac = ClientFactory(*a, **kw)
        fac.protocol = protoClass
        proto = fac.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: None
        proto.makeConnection(transport)
        return fac, proto

class BOBClientWithSetnickMixin(ProtoTestMixin):
    def test_initBOBSetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        self.assertEqual(proto.transport.value(), 'setnick spam\n')

    def test_nickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'setkeys eggs\n')

    def test_destFetchedAfterNickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'getdest\n')

    def test_nickSetWithNoKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'newkeys\n')

    def test_keypairFetchedAfterNickSetWithNoKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        self.assertEqual(proto.transport.value(), 'getkeys\n')


class TestI2PClientTunnelCreatorBOBClient(BOBClientWithSetnickMixin, unittest.TestCase):
    protocol = I2PClientTunnelCreatorBOBClient

    def test_inhostSetAfterNickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The Destination
        self.assertEqual(proto.transport.value(), 'inhost camelot\n')

    def test_inhostSetAfterNickSetWithNoKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        self.assertEqual(proto.transport.value(), 'inhost camelot\n')

    def test_inportSet(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        fac.inport = '1234'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'inport 1234\n')

    def test_startRequested(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        fac.inport = '1234'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'start\n')


class TestI2PServerTunnelCreatorBOBClient(BOBClientWithSetnickMixin, unittest.TestCase):
    protocol = I2PServerTunnelCreatorBOBClient

    def test_outhostSetAfterNickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        fac.outhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The Destination
        self.assertEqual(proto.transport.value(), 'outhost camelot\n')

    def test_outhostSetAfterNickSetWithNoKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        self.assertEqual(proto.transport.value(), 'outhost camelot\n')

    def test_outportSet(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        fac.outport = '1234'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'outport 1234\n')

    def test_startRequested(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        fac.outport = '1234'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'start\n')


class TestI2PTunnelRemoverBOBClient(ProtoTestMixin, unittest.TestCase):
    protocol = I2PTunnelRemoverBOBClient

    def test_initBOBGetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        self.assertEqual(proto.transport.value(), 'getnick spam\n')

    def test_stopRequested(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'stop\n')

    def test_clearRequested(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'clear\n')

    def test_clearRequestRepeated(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('ERROR tunnel shutting down\n')
        self.assertEqual(proto.transport.value(), 'clear\n')
