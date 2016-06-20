# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from txi2p.address import I2PAddress
from txi2p.test.util import TEST_B64, TEST_B32


class TestI2PAddress(unittest.TestCase):
    def test_noHost_noPort(self):
        addr = I2PAddress(TEST_B64)
        self.assertEqual((addr.destination, addr.host, addr.port), (TEST_B64, TEST_B32, None))

    def test_host_noPort(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p')
        self.assertEqual((addr.destination, addr.host, addr.port), (TEST_B64, 'spam.i2p', None))

    def test_noHost_port(self):
        addr = I2PAddress(TEST_B64, port=81)
        self.assertEqual((addr.destination, addr.host, addr.port), (TEST_B64, TEST_B32, 81))

    def test_host_port(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', 81)
        self.assertEqual((addr.destination, addr.host, addr.port), (TEST_B64, 'spam.i2p', 81))

    def test_portString(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', '81')
        self.assertEqual((addr.destination, addr.host, addr.port), (TEST_B64, 'spam.i2p', 81))

    def test_address_host_noPort(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', 81)
        addr2 = I2PAddress(addr, host='eggs.i2p')
        self.assertEqual((addr2.destination, addr2.host, addr2.port), (TEST_B64, 'eggs.i2p', None))

    def test_address_noHost_port(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', 81)
        addr2 = I2PAddress(addr, port=82)
        self.assertEqual((addr2.destination, addr2.host, addr2.port), (TEST_B64, 'spam.i2p', 82))

    def test_address_host_port(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', 81)
        addr2 = I2PAddress(addr, host='eggs.i2p', port=82)
        self.assertEqual((addr2.destination, addr2.host, addr2.port), (TEST_B64, 'eggs.i2p', 82))

    def test_reprWithNoHostNoPort(self):
        addr = I2PAddress(TEST_B64)
        self.assertEqual(repr(addr), 'I2PAddress(%s)' % TEST_B32)

    def test_reprWithHostNoPort(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p')
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p)')

    def test_reprWithNoHostPort(self):
        addr = I2PAddress(TEST_B64, port=81)
        self.assertEqual(repr(addr), 'I2PAddress(%s, 81)' % TEST_B32)

    def test_reprWithHostPort(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', 81)
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p, 81)')

    def test_reprWithPortString(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', '81')
        self.assertEqual(repr(addr), 'I2PAddress(spam.i2p, 81)')

    def test_hashWithNoHostNoPort(self):
        addr = I2PAddress(TEST_B64)
        self.assertEqual(hash(addr), hash((TEST_B32, None)))

    def test_hashWithHostNoPort(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p')
        self.assertEqual(hash(addr), hash(('spam.i2p', None)))

    def test_hashWithNoHostPort(self):
        addr = I2PAddress(TEST_B64, port=81)
        self.assertEqual(hash(addr), hash((TEST_B32, 81)))

    def test_hashWithHostPort(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', 81)
        self.assertEqual(hash(addr), hash(('spam.i2p', 81)))

    def test_hashWithPortString(self):
        addr = I2PAddress(TEST_B64, 'spam.i2p', '81')
        self.assertEqual(hash(addr), hash(('spam.i2p', 81)))
