# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from parsley import makeProtocol
from twisted.internet.interfaces import IListeningPort, ITransport
from twisted.internet.protocol import Protocol
from zope.interface import implementer

from txi2p import grammar
from txi2p.address import I2PAddress

DEFAULT_INPORT  = 9000
DEFAULT_OUTPORT = 9001


class BOBSender(object):
    def __init__(self, transport):
        self.transport = transport

    def sendClear(self):
        self.transport.write('clear\n')

    def sendGetdest(self):
        self.transport.write('getdest\n')

    def sendGetkeys(self):
        self.transport.write('getkeys\n')

    def sendGetnick(self, tunnelNick):
        self.transport.write('getnick %s\n' % tunnelNick)

    def sendInhost(self, inhost):
        self.transport.write('inhost %s\n' % inhost)

    def sendInport(self, inport):
        self.transport.write('inport %s\n' % inport)

    def sendList(self):
        self.transport.write('list\n')

    def sendNewkeys(self):
        self.transport.write('newkeys\n')

    def sendOption(self):
        self.transport.write('option\n')

    def sendOuthost(self, outhost):
        self.transport.write('outhost %s\n' % outhost)

    def sendOutport(self, outport):
        self.transport.write('outport %s\n' % outport)

    def sendQuiet(self):
        self.transport.write('quiet\n')

    def sendQuit(self):
        self.transport.write('quit\n')

    def sendSetkeys(self, keys):
        self.transport.write('setkeys %s\n' % keys)

    def sendSetnick(self, tunnelNick):
        self.transport.write('setnick %s\n' % tunnelNick)

    def sendShow(self):
        self.transport.write('show\n')

    def sendShowprops(self):
        self.transport.write('showprops\n')

    def sendStart(self):
        self.transport.write('start\n')

    def sendStatus(self, tunnelNick):
        self.transport.write('status %s\n' % tunnelNick)

    def sendStop(self):
        self.transport.write('stop\n')

    def sendVerify(self, key):
        self.transport.write('verify %s\n' % key)

    def sendVisit(self):
        self.transport.write('visit\n')


class BOBReceiver(object):
    currentRule = 'State_init'

    def __init__(self, sender):
        self.sender = sender
        self.tunnelExists = False

    def prepareParsing(self, parser):
        # Store the factory for later use
        self.factory = parser.factory

    def finishParsing(self, reason):
        if self.currentRule != 'State_quit':
            self.factory.bobConnectionFailed(reason)

    def initBOB(self, version):
        self.sender.sendList()
        self.currentRule = 'State_list'

    def processTunnelList(self, tunnels):
        # Default port offset is at the end of the tunnels list
        offset = 2*(len(tunnels))
        if self.factory.tunnelNick:
            for i in range(0, len(tunnels)):
                if tunnels[i]['nickname'] == self.factory.tunnelNick:
                    self.tunnelExists = True
                    self.tunnelRunning = tunnels[i]['running']
                    offset = 2*i
                    # The tunnel will be removed by the Factory
                    # that created it.
                    self.factory.removeTunnelWhenFinished = False
                    break
        else:
            self.factory.tunnelNick = 'txi2p-%d' % (len(tunnels) + 1)
        # If the in/outport were not user-configured, set them.
        if not (hasattr(self.factory, 'inport') and self.factory.inport):
            self.factory.inport = DEFAULT_INPORT + offset
        if not (hasattr(self.factory, 'outport') and self.factory.outport):
            self.factory.outport = DEFAULT_OUTPORT + offset

    def getnick(self, success, info):
        if success:
            if self.tunnelRunning:
                self.sender.sendStop()
                self.currentRule = 'State_stop'
            else:
                # Update the local Destination
                self.sender.sendGetdest()
                self.currentRule = 'State_getdest'
        else:
            print 'ERROR: %s' % info

    def stop(self, success, info):
        if success:
            # Update the local Destination
            self.sender.sendGetdest()
            self.currentRule = 'State_getdest'
        else:
            print 'stop ERROR: %s' % info

    def setnick(self, success, info):
        if success:
            if hasattr(self.factory, 'keypair') and self.factory.keypair: # If a keypair was provided, use it
                self.sender.sendSetkeys(self.factory.keypair)
                self.currentRule = 'State_setkeys'
            else: # Get a new keypair
                self.sender.sendNewkeys()
                self.currentRule = 'State_newkeys'
        else:
            print 'setnick ERROR: %s' % info

    def setkeys(self, success, info):
        if success:
            # Update the local Destination
            self.sender.sendGetdest()
            self.currentRule = 'State_getdest'
        else:
            print 'setkeys ERROR: %s' % info

    def newkeys(self, success, info):
        if success:
            # Save the new local Destination
            self.factory.localDest = info
            # Get the new keypair
            self.sender.sendGetkeys()
            self.currentRule = 'State_getkeys'
        else:
            print 'newkeys ERROR: %s' % info

    def quit(self, success, info):
        pass


class I2PClientTunnelCreatorBOBReceiver(BOBReceiver):
    def list(self, success, info, data):
        if success:
            self.processTunnelList(data)
            if self.tunnelExists:
                self.sender.sendGetnick(self.factory.tunnelNick)
                self.currentRule = 'State_getnick'
            else:
                # Set tunnel nickname (and update keypair/localDest state)
                self.sender.sendSetnick(self.factory.tunnelNick)
                self.currentRule = 'State_setnick'
        else:
            print 'list ERROR: %s' % info

    def getdest(self, success, info):
        if success:
            # Save the local Destination
            self.factory.localDest = info
            if self.tunnelExists:
                # Get the keypair
                self.sender.sendGetkeys()
                self.currentRule = 'State_getkeys'
            else:
                self._setInhost()
        else:
            print 'getdest ERROR: %s' % info

    def getkeys(self, success, info):
        if success:
            # Save the keypair
            self.factory.keypair = info
            self._setInhost()
        else:
            print 'getkeys ERROR: %s' % info

    def _setInhost(self):
        self.sender.sendInhost(self.factory.inhost)
        self.currentRule = 'State_inhost'

    def inhost(self, success, info):
        if success:
            self.sender.sendInport(self.factory.inport)
            self.currentRule = 'State_inport'
        else:
            if info in ['tunnel is active',
                        'tunnel shutting down']:
                # Try again. TODO: Limit retries
                self.sender.sendInhost(self.factory.inhost)
            else:
                print 'inhost ERROR: %s' % info

    def inport(self, success, info):
        if success:
            self.sender.sendStart()
            self.currentRule = 'State_start'
        else:
            print 'inport ERROR: %s' % info

    def start(self, success, info):
        if success:
            print "Client tunnel started"
            self.factory.i2pTunnelCreated()
            self.sender.sendQuit()
            self.currentRule = 'State_quit'
        else:
            print 'start ERROR: %s' % info


class I2PServerTunnelCreatorBOBReceiver(BOBReceiver):
    def list(self, success, info, data):
        if success:
            self.processTunnelList(data)
            if self.tunnelExists:
                self.sender.sendGetnick(self.factory.tunnelNick)
                self.currentRule = 'State_getnick'
            else:
                # Set tunnel nickname (and update keypair/localDest state)
                self.sender.sendSetnick(self.factory.tunnelNick)
                self.currentRule = 'State_setnick'
        else:
            print 'list ERROR: %s' % info

    def getdest(self, success, info):
        if success:
            # Save the local Destination
            self.factory.localDest = info
            self._setOuthost()
        else:
            print 'getdest ERROR: %s' % info

    def getkeys(self, success, info):
        if success:
            # Save the keypair
            self.factory.keypair = info
            self._setOuthost()
        else:
            print 'getkeys ERROR: %s' % info

    def _setOuthost(self):
        self.sender.sendOuthost(self.factory.outhost)
        self.currentRule = 'State_outhost'

    def outhost(self, success, info):
        if success:
            self.sender.sendOutport(self.factory.outport)
            self.currentRule = 'State_outport'
        else:
            if info in ['tunnel is active',
                        'tunnel shutting down']:
                # Try again. TODO: Limit retries
                self.sender.sendOuthost(self.factory.outhost)
            else:
                print 'outhost ERROR: %s' % info

    def outport(self, success, info):
        if success:
            self.sender.sendStart()
            self.currentRule = 'State_start'
        else:
            print 'outport ERROR: %s' % info

    def start(self, success, info):
        if success:
            print "Server tunnel started"
            self.factory.i2pTunnelCreated()
            self.sender.sendQuit()
            self.currentRule = 'State_quit'
        else:
            print 'start ERROR: %s' % info

class I2PTunnelRemoverBOBReceiver(BOBReceiver):
    def list(self, success, info, data):
        if success:
            self.processTunnelList(data)
            if self.tunnelExists:
                # Get tunnel for nickname
                self.sender.sendGetnick(self.factory.tunnelNick)
                self.currentRule = 'State_getnick'
            else:
                # Tunnel already removed
                pass
        else:
            print 'list ERROR: %s' % info

    def getnick(self, success, info):
        if success:
            self.sender.sendStop()
            self.currentRule = 'State_stop'
        else:
            print 'getnick ERROR: %s' % info

    def stop(self, success, info):
        if success:
            self.sender.sendClear()
            self.currentRule = 'State_clear'
        else:
            print 'stop ERROR: %s' % info

    def clear(self, success, info):
        if success:
            print 'Tunnel removed'
            self.factory.i2pTunnelRemoved()
            self.sender.sendQuit()
            self.currentRule = 'State_quit'
        else:
            if info in ['tunnel is active',
                        'tunnel shutting down']:
                # Try again. TODO: Limit retries
                self.sender.sendClear()
            else:
                print 'clear ERROR: %s ' % info


# A Protocol for making an I2P client tunnel via BOB
I2PClientTunnelCreatorBOBClient = makeProtocol(
    grammar.bobGrammarSource,
    BOBSender,
    I2PClientTunnelCreatorBOBReceiver)

# A Protocol for making an I2P server tunnel via BOB
I2PServerTunnelCreatorBOBClient = makeProtocol(
    grammar.bobGrammarSource,
    BOBSender,
    I2PServerTunnelCreatorBOBReceiver)

# A Protocol for removing a BOB I2P tunnel
I2PTunnelRemoverBOBClient = makeProtocol(
    grammar.bobGrammarSource,
    BOBSender,
    I2PTunnelRemoverBOBReceiver)


@implementer(ITransport)
class I2PTunnelTransport(object):
    def __init__(self, wrappedTransport, localAddr, peerAddr=None):
        self.t = wrappedTransport
        self._localAddr = localAddr
        self.peerAddr = peerAddr

    def __getattr__(self, attr):
        return getattr(self.t, attr)

    def getPeer(self):
        return self.peerAddr

    def getHost(self):
        return self._localAddr


class I2PClientTunnelProtocol(Protocol):
    def __init__(self, wrappedProto, clientAddr, dest):
        self.wrappedProto = wrappedProto
        self._clientAddr = clientAddr
        self.dest = dest

    def connectionMade(self):
        # Substitute transport for an I2P wrapper
        self.transport = I2PTunnelTransport(self.transport, self._clientAddr,
                                            I2PAddress(self.dest))
        # First line sent must be the Destination to connect to.
        self.transport.write(self.dest + '\n')
        self.wrappedProto.makeConnection(self.transport)

    def dataReceived(self, data):
        # Pass all received data to the wrapped Protocol.
        self.wrappedProto.dataReceived(data)

    def connectionLost(self, reason):
        self.factory.i2pConnectionLost(self.wrappedProto, reason)


class I2PServerTunnelProtocol(Protocol):
    def __init__(self, wrappedProto, serverAddr):
        self.wrappedProto = wrappedProto
        self._serverAddr = serverAddr
        self.peer = None

    def connectionMade(self):
        # Substitute transport for an I2P wrapper
        self.transport = I2PTunnelTransport(self.transport, self._serverAddr)
        self.wrappedProto.makeConnection(self.transport)

    def dataReceived(self, data):
        if self.peer:
            # Pass all other data to the wrapped Protocol.
            self.wrappedProto.dataReceived(data)
        else:
            # First line is the peer's Destination.
            self.peer = data.split('\n')[0]
            self.transport.peerAddr = I2PAddress(self.peer)

    def connectionLost(self, reason):
        self.wrappedProto.connectionLost(reason)


@implementer(IListeningPort)
class I2PListeningPort(object):
    def __init__(self, wrappedPort, factoryWrapper, serverAddr):
        self._wrappedPort = wrappedPort
        self._factoryWrapper = factoryWrapper
        self._serverAddr = serverAddr

    def startListening(self):
        self._wrappedPort.startListening()

    def stopListening(self):
        self._factoryWrapper.stopListening(self._wrappedPort)

    def getHost(self):
        return self._serverAddr
