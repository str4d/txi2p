from zope.interface import implementer

from twisted.internet.interfaces import IStreamServerEndpoint


@implementer(IStreamServerEndpoint)
class I2PServerEndpoint(object):
    """
    I2P server endpoint.
    """

    # TODO: Implement properly
    def __init__(self, STUFF, bobEndpoint):
        self.STUFF = STUFF
        self.bobEndpoint = bobEndpoint

    def listen(self, fac):
        """
        Listen over I2P.

        The provided factory will have its ``buildProtocol`` method called once
        an I2P server tunnel has been successfully created.

        If the factory's ``buildProtocol`` returns ``None``, the connection
        will immediately close.
        """

        i2pFac = I2PServerFactory(self.STUFF, fac) # TODO: Implement properly
        d = self.bobEndpoint.connect(i2pFac)
        d.addCallback(lambda proto: i2pFac.deferred)
        return d
