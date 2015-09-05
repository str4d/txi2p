# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from parsley import makeProtocol
from twisted.internet.defer import Deferred
from twisted.internet.error import ConnectError, UnknownHostError
from twisted.internet.interfaces import IListeningPort, ITransport
from zope.interface import implementer

from txi2p import grammar
from txi2p.address import I2PAddress
from txi2p.sam.base import SAMSender, SAMReceiver, SAMFactory


class StreamConnectSender(SAMSender):
    def sendStreamConnect(self, id, destination, silent=False):
        msg = 'STREAM CONNECT'
        msg += ' ID=%s' % id
        msg += ' DESTINATION=%s' % destination
        msg += ' SILENT=%s' % str(silent).lower()
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
            self.factory.session.id, self.factory.dest)
        self.currentRule = 'State_connect'

    def connect(self, result, message=None):
        if result != 'OK':
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

    def __init__(self, clientFactory, session, host, dest):
        self._clientFactory = clientFactory
        self.session = session
        self.host = host
        self.dest = dest
        self.deferred = Deferred(self._cancel);

    def streamConnectionEstablished(self, streamProto):
        proto = self._clientFactory.buildProtocol(I2PAddress(self.dest, self.host))
        if proto is None:
            self.deferred.cancel()
            return
        streamProto.wrapProto(proto)
        self.deferred.callback(proto)
