# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from txi2p.address import I2PAddress

TEST_B64 = "2wDRF5nDfeTNgM4X-TI5xEk3R-WiaTABvkMQ2eYpvEzayUZQJgr9E2T6Y2m9HHn3xHYGEOg-RLisjW9AubTaUTx-v66AsEEtv745qPcuWuV1SP~w1bdzYEn8MSoK7Zh4mwHBg1uHq8z17TUNvWz19q76vHNth-2PDuBToD7ySBn3cGBFDUU83wJJXPD6OueLY8yosWWtksk7WZk60~6z~nVePPSEY8JDry3myLDe11szAVER4A8eX1sFpw247cXGGJK9wQhV-TXFj~m76GPVcFKh7u79zwTwZnZ1GXXKqqyRoj1c4-U69CvvJsQRLmdLFwFEpRkxwV8z6LIFclYJk443YpTnPXC7vNdFOzqqS4FLR1ra~DNfN5foMtR2~2VxuR5m2dYiOS6GzHDxA4acJJSGqnasJjcEIFNVSQKxMnFu9PvGLNJHZ83EraHCErENcOGkPlnVgcJCtPGNGiirwCbBz38jE0lfjkrNrWabc6uWeU559CobG8F8KUDx1irpAAAA"
TEST_B32 = "tv5iv4i5roywnv2rg6rjqufniqbogn4rokjkooa7n4jht3lex3ga.b32.i2p"


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
