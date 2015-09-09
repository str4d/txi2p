# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.interfaces import IListeningPort, IProtocolFactory
from twisted.internet.protocol import ClientFactory
from twisted.python.failure import Failure
from zope.interface import implementer

from txi2p.address import (
    I2PAddress,
    I2PServerTunnelProtocol,
    I2PTunnelTransport,
)
from txi2p.sam import constants as c


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
            self.factory.session.address,
            I2PAddress(self.factory.dest, self.factory.host))
        proto.makeConnection(self.transportWrapper)

    def dataReceived(self, data):
        self.wrappedProto.dataReceived(data)

    def finishParsing(self, reason):
        if self.wrappedProto:
            self.wrappedProto.connectionLost(reason)
        else:
            self.factory.connectionFailed(reason)
        if hasattr(self.factory, 'session'):
            self.factory.session.removeStream(self)

    def hello(self, result, version=None, message=None):
        if result != c.RESULT_OK:
            self.factory.resultNotOK(result, message)
            return
        self.command()

    def lookupReply(self, result, name, value=None, message=None):
        if result != c.RESULT_OK:
            self.factory.resultNotOK(result, message)
            return
        self.postLookup(value)


class SAMFactory(ClientFactory):
    currentCandidate = None
    canceled = False

    def _cancel(self, d):
        self.currentCandidate.sender.transport.abortConnection()
        self.canceled = True

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        self.currentCandidate = proto
        return proto

    def connectionFailed(self, reason):
        if not self.canceled and not self.deferred.called:
            self.deferred.errback(reason)

    # This method is not called if an endpoint deferred errbacks
    def clientConnectionFailed(self, connector, reason):
        self.connectionFailed(reason)

    def resultNotOK(self, result, message):
        raise c.samErrorMap.get(result)(string=(message if message else result))


@implementer(IProtocolFactory)
class I2PFactoryWrapper(object):
    protocol = I2PServerTunnelProtocol

    def __init__(self, wrappedFactory, serverAddr):
        self.w = wrappedFactory
        self.serverAddr = serverAddr

    def buildProtocol(self, addr):
        wrappedProto = self.w.buildProtocol(addr)
        proto = self.protocol(wrappedProto, self.serverAddr)
        proto.factory = self
        return proto

    def __getattr__(self, attr):
        return getattr(self.w, attr)


@implementer(IListeningPort)
class I2PListeningPort(object):
    def __init__(self, listeningPort, forwardingProto, serverAddr):
        self._listeningPort = listeningPort
        self._forwardingProto = forwardingProto
        self._serverAddr = serverAddr

    def startListening(self):
        self._listeningPort.startListening()

    def stopListening(self):
        self._listeningPort.stopListening()
        self._forwardingProto.sender.transport.loseConnection()

    def getHost(self):
        return self._serverAddr
