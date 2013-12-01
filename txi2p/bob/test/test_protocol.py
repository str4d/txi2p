# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.protocol import ClientFactory
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.bob.protocol import (I2PClientTunnelCreatorBOBClient,
                                I2PServerTunnelCreatorBOBClient,
                                I2PTunnelRemoverBOBClient,
                                I2PClientTunnelProtocol,
                                I2PServerTunnelProtocol,
                                DEFAULT_INPORT, DEFAULT_OUTPORT)


class BOBProtoTestMixin(object):
    def makeProto(self, *a, **kw):
        protoClass = kw.pop('_protoClass', self.protocol)
        fac = ClientFactory(*a, **kw)
        fac.protocol = protoClass
        proto = fac.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: None
        proto.makeConnection(transport)
        return fac, proto

    def test_initBOBListsTunnels(self):
        fac, proto = self.makeProto()
        proto.dataReceived('BOB 00.00.10\nOK\n')
        self.assertEqual(proto.transport.value(), 'list\n')

    def TODO_test_quitDoesNotErrback(self):
        fac, proto = self.makeProto()
        # Shortcut to end of BOB protocol
        proto.receiver.currentRule = 'State_quit'
        proto._parser._setupInterp()
        proto.dataReceived('OK Bye!\n')
        self.assertTrue(False, 'TODO: Test something') # TODO: Test something

class BOBTunnelCreationMixin(BOBProtoTestMixin):
    def test_defaultNickSetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = None
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        self.assertEqual(proto.transport.value(), 'setnick txi2p-1\n')

    def test_newNickSetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        self.assertEqual(proto.transport.value(), 'setnick spam\n')

    def test_nickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'setkeys eggs\n')

    def test_destFetchedAfterNickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'newkeys\n')

    def test_keypairFetchedAfterNickSetWithNoKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        self.assertEqual(proto.transport.value(), 'getkeys\n')

    def test_existingNickGetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nOK Listing done\n')
        self.assertEqual(proto.transport.value(), 'getnick spam\n')

    def test_stopRequestedForRunningTunnel(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nOK Listing done\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'stop\n')

    def test_stopNotRequestedForStoppedTunnel(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: false STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nOK Listing done\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertNotEqual(proto.transport.value(), 'stop\n') # TODO: Refactor to test against what is actually expected

    def test_quitRequestedAfterStart(self):
        fac, proto = self.makeProto()
        called = []
        fac.i2pTunnelCreated = lambda: called.append(True)
        # Shortcut
        proto.receiver.currentRule = 'State_start'
        proto._parser._setupInterp()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual((called, proto.transport.value()), ([True], 'quit\n'))

class TestI2PClientTunnelCreatorBOBClient(BOBTunnelCreationMixin, unittest.TestCase):
    protocol = I2PClientTunnelCreatorBOBClient

    def test_inhostRequestRepeatedIfActive(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        # Shortcut
        proto.receiver.currentRule = 'State_inhost'
        proto._parser._setupInterp()
        proto.dataReceived('ERROR tunnel is active\n')
        self.assertEqual(proto.transport.value(), 'inhost camelot\n')

    def test_inhostRequestRepeatedIfShuttingDown(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        # Shortcut
        proto.receiver.currentRule = 'State_inhost'
        proto._parser._setupInterp()
        proto.dataReceived('ERROR tunnel shutting down\n')
        self.assertEqual(proto.transport.value(), 'inhost camelot\n')

    def test_inhostSetAfterNickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        self.assertEqual(proto.transport.value(), 'inhost camelot\n')

    def test_defaultInportSet(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'inport %s\n' % DEFAULT_INPORT)

    def test_inportSet(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        fac.inport = '1234'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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


class TestI2PServerTunnelCreatorBOBClient(BOBTunnelCreationMixin, unittest.TestCase):
    protocol = I2PServerTunnelCreatorBOBClient

    def test_outhostRequestRepeatedIfActive(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        # Shortcut
        proto.receiver.currentRule = 'State_outhost'
        proto._parser._setupInterp()
        proto.dataReceived('ERROR tunnel is active\n')
        self.assertEqual(proto.transport.value(), 'outhost camelot\n')

    def test_outhostRequestRepeatedIfShuttingDown(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        # Shortcut
        proto.receiver.currentRule = 'State_outhost'
        proto._parser._setupInterp()
        proto.dataReceived('ERROR tunnel shutting down\n')
        self.assertEqual(proto.transport.value(), 'outhost camelot\n')

    def test_outhostSetAfterNickSetWithKeypair(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.keypair = 'eggs'
        fac.outhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        self.assertEqual(proto.transport.value(), 'outhost camelot\n')

    def test_defaultOutportSet(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK shrubbery\n') # The new Destination
        proto.transport.clear()
        proto.dataReceived('OK rubberyeggs\n') # The new keypair
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'outport %s\n' % DEFAULT_OUTPORT)

    def test_outportSet(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        fac.outport = '1234'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
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


class TestI2PTunnelRemoverBOBClient(BOBProtoTestMixin, unittest.TestCase):
    protocol = I2PTunnelRemoverBOBClient

    def test_noTunnelWithNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        self.assertEqual(proto.transport.value(), '')

    def test_tunnelExistsGetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nOK Listing done\n')
        self.assertEqual(proto.transport.value(), 'getnick spam\n')

    def test_stopRequested(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nOK Listing done\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'stop\n')

    def test_clearRequested(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nOK Listing done\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        proto.transport.clear()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'clear\n')

    def test_clearRequestRepeatedIfActive(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        # Shortcut
        proto.receiver.currentRule = 'State_clear'
        proto._parser._setupInterp()
        proto.dataReceived('ERROR tunnel is active\n')
        self.assertEqual(proto.transport.value(), 'clear\n')

    def test_clearRequestRepeatedIfShuttingDown(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        # Shortcut
        proto.receiver.currentRule = 'State_clear'
        proto._parser._setupInterp()
        proto.dataReceived('ERROR tunnel shutting down\n')
        self.assertEqual(proto.transport.value(), 'clear\n')

    def test_quitRequestedAfterClearSuccess(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.i2pTunnelRemoved = lambda: None
        # Shortcut
        proto.receiver.currentRule = 'State_clear'
        proto._parser._setupInterp()
        proto.dataReceived('OK HTTP 418\n')
        self.assertEqual(proto.transport.value(), 'quit\n')


class TestI2PClientTunnelProtocol(unittest.TestCase):
    def makeProto(self):
        wrappedProto = proto_helpers.AccumulatingProtocol()
        proto = I2PClientTunnelProtocol(wrappedProto, None, 'spam.i2p')
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: None
        proto.makeConnection(transport)
        return proto

    def test_destRequested(self):
        proto = self.makeProto()
        self.assertEqual(proto.transport.value(), 'spam.i2p\n')

    def test_wrappedProtoConnectionMade(self):
        proto = self.makeProto()
        self.assertEqual(proto.transport, proto.wrappedProto.transport)

    def test_dataPassed(self):
        proto = self.makeProto()
        proto.dataReceived('shrubbery')
        self.assertEqual(proto.wrappedProto.data, 'shrubbery')


class TestI2PServerTunnelProtocol(unittest.TestCase):
    def makeProto(self):
        wrappedProto = proto_helpers.AccumulatingProtocol()
        proto = I2PServerTunnelProtocol(wrappedProto, None)
        transport = proto_helpers.StringTransport()
        transport.abortConnection = lambda: None
        proto.makeConnection(transport)
        return proto

    def test_wrappedProtoConnectionMade(self):
        proto = self.makeProto()
        self.assertEqual(proto.transport, proto.wrappedProto.transport)

    def test_peerDestStored(self):
        proto = self.makeProto()
        proto.dataReceived('spam.i2p\n')
        self.assertEqual(proto.peer, 'spam.i2p')

    def test_dataAfterPeerDestPassed(self):
        proto = self.makeProto()
        proto.dataReceived('spam.i2p\n')
        proto.dataReceived('shrubbery')
        self.assertEqual(proto.wrappedProto.data, 'shrubbery')
