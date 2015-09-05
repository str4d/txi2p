# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from txi2p.address import I2PAddress


class TestI2PAddress(unittest.TestCase):
    def test_noHost_noPort(self):
        addr = I2PAddress('DESTINATION')
        self.assertEqual((addr.destination, addr.host, addr.port), ('DESTINATION', None, None))

    def test_host_noPort(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p')
        self.assertEqual((addr.destination, addr.host, addr.port), ('DESTINATION', 'spam.i2p', None))

    def test_noHost_port(self):
        addr = I2PAddress('DESTINATION', port=81)
        self.assertEqual((addr.destination, addr.host, addr.port), ('DESTINATION', None, 81))

    def test_host_port(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p', 81)
        self.assertEqual((addr.destination, addr.host, addr.port), ('DESTINATION', 'spam.i2p', 81))

    def test_portString(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p', '81')
        self.assertEqual((addr.destination, addr.host, addr.port), ('DESTINATION', 'spam.i2p', 81))

    def test_reprWithNoHostNoPort(self):
        addr = I2PAddress('DESTINATION')
        self.assertEqual(repr(addr), 'I2PAddress(DESTINATION)')

    def test_reprWithHostNoPort(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p')
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p)')

    def test_reprWithNoHostPort(self):
        addr = I2PAddress('DESTINATION', port=81)
        self.assertEqual(repr(addr), 'I2PAddress(DESTINATION, 81)')

    def test_reprWithHostPort(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p', 81)
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p, 81)')

    def test_reprWithPortString(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p', '81')
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p, 81)')

    def test_hashWithNoHostNoPort(self):
        addr = I2PAddress('DESTINATION')
        self.assertEqual(hash(addr), hash(('DESTINATION', None)))

    def test_hashWithHostNoPort(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p')
        self.assertEqual(hash(addr), hash(('DESTINATION', None)))

    def test_hashWithNoHostPort(self):
        addr = I2PAddress('DESTINATION', port=81)
        self.assertEqual(hash(addr), hash(('DESTINATION', 81)))

    def test_hashWithHostPort(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p', 81)
        self.assertEqual(hash(addr), hash(('DESTINATION', 81)))

    def test_hashWithPortString(self):
        addr = I2PAddress('DESTINATION', 'spam.i2p', '81')
        self.assertEqual(hash(addr), hash(('DESTINATION', 81)))
