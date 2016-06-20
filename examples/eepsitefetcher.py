from sys import stdout
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from twisted.internet.protocol import ClientFactory, Protocol


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


endpoint = clientFromString(reactor, 'i2p:stats.i2p:81')
d = endpoint.connect(EepsiteFactory())

reactor.run()
