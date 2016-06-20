from twisted.internet import reactor, defer
from twisted.internet.endpoints import serverFromString
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class Answer(LineReceiver):
    answers = {
        'How are you?': 'Fine',
        'W007!': 'INORITE?',
        None : "I don't know what you mean",
        }

    def lineReceived(self, line):
        print 'Line received from %s' % self.transport.getPeer()
        if self.answers.has_key(line):
            self.sendLine(self.answers[line])
        else:
            self.sendLine(self.answers[None])


class AnswerFactory(Factory):
    protocol = Answer


def printDest(port):
    # Print out the I2P Destination to copy to the client
    print 'This server is listening on:'
    print port.getHost().destination
    # Handle Ctl+C
    def shutdown():
        print 'Shutting down'
        port.stopListening()
        d = defer.Deferred()
        reactor.callLater(3, d.callback, 1)
        return d
    reactor.addSystemEventTrigger('before', 'shutdown', shutdown)


endpoint = serverFromString(reactor, 'i2p:keypair.answerserver')
d = endpoint.listen(AnswerFactory())
d.addCallback(printDest)

reactor.run()
