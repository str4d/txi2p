# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.protocol import ClientFactory
from twisted.python.failure import Failure

from txi2p.address import I2PAddress, I2PTunnelTransport


class SAMSender(object):
    def __init__(self, transport):
        self.transport = transport

    def sendHello(self):
        self.transport.write('HELLO VERSION MIN=3.0 MAX=3.1\n')

    def sendNamingLookup(self, name):
        self.transport.write('NAMING LOOKUP NAME=%s\n' % name)


class SAMReceiver(object):
    wrappedProto = None
    currentRule = 'State_hello'

    def __init__(self, sender):
        self.sender = sender

    def prepareParsing(self, parser):
        # Store the factory for later use
        self.factory = parser.factory
        self.sender.sendHello()

    def wrapProto(self, proto):
        self.wrappedProto = proto
        self.transportWrapper = I2PTunnelTransport(
            self.sender.transport,
            I2PAddress(self.factory.session.pubKey),
            I2PAddress(self.factory.dest, self.factory.host))
        proto.makeConnection(self.transportWrapper)

    def dataReceived(self, data):
        self.wrappedProto.dataReceived(data)

    def finishParsing(self, reason):
        if self.wrappedProto:
            self.wrappedProto.connectionLost(reason)
        else:
            self.factory.connectionFailed(reason)

    def hello(self, result, version=None, message=None):
        if result != 'OK':
            self.factory.resultNotOK(result, message)
            return
        self.command()

    def lookupReply(self, result, name, value=None, message=None):
        if result != 'OK':
            self.factory.resultNotOK(result, message)
            return
        self.postLookup(value)


class SAMFactory(ClientFactory):
    currentCandidate = None
    canceled = False

    def _cancel(self, d):
        self.currentCandidate.sender.transport.abortConnection()
        self.canceled = True

    def buildProto(self, addr):
        proto = self.protocol
        proto.factory = self
        self.currentCandidate = proto
        return proto

    def connectionFailed(self, reason):
        if not self.canceled and not self.deferred.called:
            self.deferred.errback(reason)

    def resultNotOK(self, result, message):
        self.connectionFailed(Failure(Exception('%s: %s' % (result, message))))

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.connectionFailed(reason)
