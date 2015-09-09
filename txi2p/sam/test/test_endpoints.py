# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.error import ConnectionLost, ConnectionRefusedError
from twisted.python import failure
from twisted.trial import unittest

from txi2p.sam import endpoints
from txi2p.test.util import FakeEndpoint, FakeFactory


connectionLostFailure = failure.Failure(ConnectionLost())
connectionRefusedFailure = failure.Failure(ConnectionRefusedError())



class SAMI2PStreamClientEndpointTestCase(unittest.TestCase):
    """
    Tests for I2P client Endpoint backed by the SAM API.
    """

    def test_samConnectionFailed(self):
        reactor = object()
        samEndpoint = FakeEndpoint(failure=connectionRefusedFailure)
        endpoint = endpoints.SAMI2PStreamClientEndpoint(samEndpoint, '')
        d = endpoint.connect(None)
        return self.assertFailure(d, ConnectionRefusedError)
