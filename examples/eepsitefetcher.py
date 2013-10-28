from sys import stdout
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from twisted.internet.protocol import ClientFactory, Protocol

from txi2p.bob.endpoints import BOBI2PClientEndpoint


class Eepsite(Protocol):
    def connectionMade(self):
        print 'Connection made, sending eepsite request'
        self.transport.write('GET / HTTP/1.1\r\n\r\n')

    def dataReceived(self, data):
        stdout.write(data)

    def connectionLost(self, reason):
        print 'Lost connection.  Reason:', reason
        reactor.stop()


class EepsiteFactory(ClientFactory):
    protocol = Eepsite


bobEndpoint = clientFromString(reactor, 'tcp:127.0.0.1:2827')
endpoint = BOBI2PClientEndpoint(reactor, bobEndpoint, 'stats.i2p')
d = endpoint.connect(EepsiteFactory())

reactor.run()
