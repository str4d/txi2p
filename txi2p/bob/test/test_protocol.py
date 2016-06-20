# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import os
from twisted.internet.error import UnknownHostError
from twisted.internet.protocol import ClientFactory
from twisted.python.failure import Failure
from twisted.test import proto_helpers
from twisted.trial import unittest

from txi2p.bob.protocol import (I2PClientTunnelCreatorBOBClient,
                                I2PServerTunnelCreatorBOBClient,
                                I2PTunnelRemoverBOBClient,
                                I2PClientTunnelProtocol,
                                I2PServerTunnelProtocol,
                                DEFAULT_INPORT, DEFAULT_OUTPORT)

TEST_B64 = "2wDRF5nDfeTNgM4X-TI5xEk3R-WiaTABvkMQ2eYpvEzayUZQJgr9E2T6Y2m9HHn3xHYGEOg-RLisjW9AubTaUTx-v66AsEEtv745qPcuWuV1SP~w1bdzYEn8MSoK7Zh4mwHBg1uHq8z17TUNvWz19q76vHNth-2PDuBToD7ySBn3cGBFDUU83wJJXPD6OueLY8yosWWtksk7WZk60~6z~nVePPSEY8JDry3myLDe11szAVER4A8eX1sFpw247cXGGJK9wQhV-TXFj~m76GPVcFKh7u79zwTwZnZ1GXXKqqyRoj1c4-U69CvvJsQRLmdLFwFEpRkxwV8z6LIFclYJk443YpTnPXC7vNdFOzqqS4FLR1ra~DNfN5foMtR2~2VxuR5m2dYiOS6GzHDxA4acJJSGqnasJjcEIFNVSQKxMnFu9PvGLNJHZ83EraHCErENcOGkPlnVgcJCtPGNGiirwCbBz38jE0lfjkrNrWabc6uWeU559CobG8F8KUDx1irpAAAA"


class BOBProtoTestMixin(object):
    def makeProto(self, *a, **kw):
        protoClass = kw.pop('_protoClass', self.protocol)
        fac = ClientFactory(*a, **kw)
        fac.protocol = protoClass
        def raise_(ex):
            raise ex
        fac.bobConnectionFailed = lambda reason: raise_(reason)
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
    def test_defaultInportSelected(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        self.assertTrue(hasattr(fac, 'inport'))
        self.assertEqual(fac.inport, DEFAULT_INPORT)

    def test_higherInportSelectedWhenDefaultBusy(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: test STARTING: false RUNNING: false STOPPING: false KEYS: false QUIET: false INPORT: 9000 INHOST: localhost OUTPORT: not_set OUTHOST: localhost\nOK Listing done\n')
        self.assertTrue(hasattr(fac, 'inport'))
        self.assertEqual(fac.inport, DEFAULT_INPORT + 2)

    def test_existingInhostAndInportSelectedForExistingTunnel(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        fac.inport = 1234
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: false STOPPING: false KEYS: false QUIET: false INPORT: 2345 INHOST: localhost OUTPORT: not_set OUTHOST: localhost\nOK Listing done\n')
        self.assertEqual(fac.inhost, 'localhost')
        self.assertEqual(fac.inport, 2345)

    def test_defaultOutportSelected(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.inhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        self.assertTrue(hasattr(fac, 'outport'))
        self.assertEqual(fac.outport, DEFAULT_OUTPORT)

    def test_higherOutportSelectedWhenDefaultBusy(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: test STARTING: false RUNNING: false STOPPING: false KEYS: false QUIET: false INPORT: not_set INHOST: localhost OUTPORT: 9001 OUTHOST: localhost\nOK Listing done\n')
        self.assertTrue(hasattr(fac, 'outport'))
        self.assertEqual(fac.outport, DEFAULT_OUTPORT + 2)

    def test_existingOuthostAndOutportSelectedForExistingTunnel(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = 'spam'
        fac.outhost = 'camelot'
        fac.outport = 1234
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('DATA NICKNAME: spam STARTING: false RUNNING: false STOPPING: false KEYS: false QUIET: false INPORT: not_set INHOST: localhost OUTPORT: 2345 OUTHOST: localhost\nOK Listing done\n')
        self.assertEqual(fac.outhost, 'localhost')
        self.assertEqual(fac.outport, 2345)

    def test_defaultNickSetsNick(self):
        fac, proto = self.makeProto()
        fac.tunnelNick = None
        proto.dataReceived('BOB 00.00.10\nOK\n')
        proto.transport.clear()
        proto.dataReceived('OK Listing done\n') # No DATA, no tunnels
        self.assertEqual(proto.transport.value(), 'setnick txi2p-%d\n' % os.getpid())

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
        self.assertEqual(proto.transport.value(), 'inport %d\n' % DEFAULT_INPORT)

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
        self.assertEqual(proto.transport.value(), 'outport %d\n' % DEFAULT_OUTPORT)

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


class FakeDisconnectingFactory(object):
    def i2pConnectionLost(self, wrappedProto, reason):
        wrappedProto.connectionLost(reason)

class TestI2PClientTunnelProtocol(unittest.TestCase):
    def makeProto(self):
        wrappedProto = proto_helpers.AccumulatingProtocol()
        proto = I2PClientTunnelProtocol(wrappedProto, None, TEST_B64)
        proto.factory = FakeDisconnectingFactory()
        transport = proto_helpers.StringTransportWithDisconnection()
        transport.abortConnection = lambda: None
        transport.protocol = proto
        proto.makeConnection(transport)
        return proto

    def test_destRequested(self):
        proto = self.makeProto()
        self.assertEqual(proto.transport.value(), '%s\n' % TEST_B64)

    def test_wrappedProtoConnectionMade(self):
        proto = self.makeProto()
        self.assertEqual(proto.transport, proto.wrappedProto.transport)

    def test_connectionFailed(self):
        proto = self.makeProto()
        proto.dataReceived("ERROR Can't find destination: spam.i2p")
        self.assertEqual(proto.wrappedProto.closed, 1)

        expected = UnknownHostError(string="Can't find destination: spam.i2p")
        got = proto.wrappedProto.closedReason.value
        self.assertEqual(type(expected), type(got))
        self.assertEqual(expected.args, got.args)

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
        proto.dataReceived('%s\n' % TEST_B64)
        self.assertEqual(proto.peer.destination, TEST_B64)

    def test_dataAfterPeerDestPassed(self):
        proto = self.makeProto()
        proto.dataReceived('%s\n' % TEST_B64)
        proto.dataReceived('shrubbery')
        self.assertEqual(proto.wrappedProto.data, 'shrubbery')
