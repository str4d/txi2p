from __future__ import print_function
from twisted.internet import reactor, defer
from twisted.internet.endpoints import serverFromString
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        self.sendLine("What's your name?")

    def connectionLost(self, reason):
        if self.users.has_key(self.name):
            del self.users[self.name]

    def lineReceived(self, line):
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if self.users.has_key(name):
            self.sendLine("Name taken, please choose another.")
            return
        self.sendLine("Welcome, %s!" % (name,))
        self.name = name
        self.users[name] = self
        self.state = "CHAT"

    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)


def printDest(port):
    # Print out the I2P Destination to copy to the client
    print('This server is listening on:')
    print(port.getHost().destination)
    # Handle Ctl+C
    def shutdown():
        print('Shutting down')
        port.stopListening()
        d = defer.Deferred()
        reactor.callLater(3, d.callback, 1)
        return d
    reactor.addSystemEventTrigger('before', 'shutdown', shutdown)


endpoint = serverFromString(reactor, 'i2p:keypair.chatserver')
d = endpoint.listen(ChatFactory())
d.addCallback(printDest)

reactor.run()
