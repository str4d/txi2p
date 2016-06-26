# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from parsley import makeProtocol
from twisted.internet.defer import Deferred
from twisted.internet.error import ConnectError, UnknownHostError
from twisted.internet.interfaces import IListeningPort
from zope.interface import implementer

from txi2p import grammar
from txi2p.address import I2PAddress
from txi2p.sam import constants as c
from txi2p.sam.base import (
    cmpSAM,
    peerSAM,
    SAMSender,
    SAMReceiver,
    SAMFactory,
)


class StreamConnectSender(SAMSender):
    def sendStreamConnect(self, id, destination, port=None, localPort=None):
        msg = 'STREAM CONNECT'
        msg += ' ID=%s' % id
        msg += ' DESTINATION=%s' % destination
        msg += ' SILENT=false'
        if port:
            msg += ' TO_PORT=%d' % port
        if localPort:
            msg += ' FROM_PORT=%d' % localPort
        msg += '\n'
        self.transport.write(msg)


class StreamConnectReceiver(SAMReceiver):
    def command(self):
        if self.factory.dest:
            self.doConnect()
        else:
            self.sender.sendNamingLookup(self.factory.host)
            self.currentRule = 'State_naming'

    def postLookup(self, dest):
        self.factory.dest = dest
        self.doConnect()

    def doConnect(self):
        self.sender.sendStreamConnect(
            self.factory.session.id, self.factory.dest,
            self.factory.port, self.factory.localPort)
        self.currentRule = 'State_connect'

    def connect(self, result, message=None):
        if result != c.RESULT_OK:
            self.factory.resultNotOK(result, message)
            return

        self.factory.streamConnectionEstablished(self)
        self.currentRule = 'State_readData'


StreamConnectProtocol = makeProtocol(
    grammar.samGrammarSource,
    StreamConnectSender,
    StreamConnectReceiver)


class StreamConnectFactory(SAMFactory):
    protocol = StreamConnectProtocol

    def __init__(self, clientFactory, session, host, dest, port=None, localPort=None):
        self._clientFactory = clientFactory
        self.session = session
        self.host = host
        self.dest = dest
        self.port = port
        self.localPort = localPort
        self.deferred = Deferred(self._cancel);

    def streamConnectionEstablished(self, streamProto):
        self.session.addStream(streamProto)
        peerAddress = I2PAddress(self.dest, self.host, self.port)
        proto = self._clientFactory.buildProtocol(peerAddress)
        if proto is None:
            self.deferred.cancel()
            return
        streamProto.wrapProto(proto, peerAddress)
        self.deferred.callback(proto)


class StreamAcceptSender(SAMSender):
    def sendStreamAccept(self, id):
        msg = 'STREAM ACCEPT'
        msg += ' ID=%s' % id
        msg += ' SILENT=false'
        msg += '\n'
        self.transport.write(msg)


class StreamAcceptReceiver(SAMReceiver):
    peer = None
    initialData = ''

    def command(self):
        self.sender.sendStreamAccept(
            self.factory.session.id)
        self.currentRule = 'State_accept'

    def accept(self, result, message=None):
        if result != c.RESULT_OK:
            self.factory.resultNotOK(result, message)
            return
        self.factory.streamAcceptEstablished(self)
        self.currentRule = 'State_readData'

    def dataReceived(self, data):
        if self.peer:
            # Pass all other data to the wrapped Protocol.
            if self.initialData:
                data = self.initialData + data
                self.initialData = None
            self.wrappedProto.dataReceived(data)
        else:
            self.initialData += data
            if '\n' in self.initialData:
                # First line is the peer's Destination.
                data, self.initialData = self.initialData.split('\n', 1)
                self.peer = peerSAM(data)
                self.factory.streamAcceptIncoming(self)


StreamAcceptProtocol = makeProtocol(
    grammar.samGrammarSource,
    StreamAcceptSender,
    StreamAcceptReceiver)


class StreamAcceptFactory(SAMFactory):
    protocol = StreamAcceptProtocol

    def __init__(self, clientFactory, session, listeningPort):
        self._clientFactory = clientFactory
        self.session = session
        self.listeningPort = listeningPort
        self.deferred = Deferred(self._cancel);

    def streamAcceptEstablished(self, streamProto):
        self.session.addStream(streamProto)
        self.listeningPort.addAccept(streamProto)

    def streamAcceptIncoming(self, streamProto):
        self.listeningPort.removeAccept(streamProto)
        proto = self._clientFactory.buildProtocol(streamProto.peer)
        if proto is None:
            self.deferred.cancel()
            return
        streamProto.wrapProto(proto, streamProto.peer)


@implementer(IListeningPort)
class StreamAcceptPort(object):
    def __init__(self, session, factory):
        self.session = session
        self.factory = StreamAcceptFactory(factory, session, self)
        self.accepts = []

    def startListening(self):
        if cmpSAM(self.session.samVersion, '3.2') >= 0:
            active = 8
        else:
            active = 1
        for i in range(0, active):
            self.openAccept()

    def stopListening(self):
        for pending in self.accepts:
            pending.sender.transport.loseConnection()
        self.accepts = []

    def openAccept(self):
        self.session.samEndpoint.connect(self.factory)

    def addAccept(self, proto):
        self.accepts.append(proto)

    def removeAccept(self, proto):
        self.accepts.remove(proto)
        self.openAccept()

    def getHost(self):
        return self.session.address


class StreamForwardSender(SAMSender):
    def sendStreamForward(self, id, port, host=None):
        msg = 'STREAM FORWARD'
        msg += ' ID=%s' % id
        msg += ' PORT=%s' % port
        if host:
            msg += ' HOST=%s' % host
        msg += ' SILENT=false'
        msg += '\n'
        self.transport.write(msg)


class StreamForwardReceiver(SAMReceiver):
    def command(self):
        self.sender.sendStreamForward(
            self.factory.session.id,
            self.factory.forwardPort)
        self.currentRule = 'State_forward'

    def forward(self, result, message=None):
        if result != c.RESULT_OK:
            self.factory.resultNotOK(result, message)
            return
        self.factory.streamForwardEstablished(self)


StreamForwardProtocol = makeProtocol(
    grammar.samGrammarSource,
    StreamForwardSender,
    StreamForwardReceiver)


class StreamForwardFactory(SAMFactory):
    protocol = StreamForwardProtocol

    def __init__(self, session, forwardPort):
        self.session = session
        self.forwardPort = forwardPort
        self.deferred = Deferred(self._cancel);

    def streamForwardEstablished(self, forwardingProto):
        self.session.addStream(forwardingProto)
        self.deferred.callback(forwardingProto)


@implementer(IListeningPort)
class StreamForwardPort(object):
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
