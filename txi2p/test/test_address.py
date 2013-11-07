# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from txi2p.address import I2PAddress


class TestI2PAddress(unittest.TestCase):
    def test_noPort(self):
        addr = I2PAddress('spam.i2p')
        self.assertEqual((addr.destination, addr.port), ('spam.i2p', None))

    def test_port(self):
        addr = I2PAddress('spam.i2p', 81)
        self.assertEqual((addr.destination, addr.port), ('spam.i2p', 81))

    def test_portString(self):
        addr = I2PAddress('spam.i2p', '81')
        self.assertEqual((addr.destination, addr.port), ('spam.i2p', 81))

    def test_reprWithNoPort(self):
        addr = I2PAddress('spam.i2p')
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p)')

    def test_reprWithPort(self):
        addr = I2PAddress('spam.i2p', 81)
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p, 81)')

    def test_reprWithPortString(self):
        addr = I2PAddress('spam.i2p', '81')
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p, 81)')

    def test_hashWithNoPort(self):
        addr = I2PAddress('spam.i2p')
        self.assertEqual(hash(addr), hash(('spam.i2p',None)))

    def test_hashWithPort(self):
        addr = I2PAddress('spam.i2p', 81)
        self.assertEqual(hash(addr), hash(('spam.i2p', 81)))

    def test_hashWithPortString(self):
        addr = I2PAddress('spam.i2p', '81')
        self.assertEqual(hash(addr), hash(('spam.i2p', 81)))
