# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import os
from parsley import makeProtocol
from twisted.internet.error import ConnectError, UnknownHostError
from twisted.internet.interfaces import IListeningPort
from twisted.internet.protocol import Protocol
from twisted.python.failure import Failure
from zope.interface import implementer

from txi2p import grammar
from txi2p.address import (
    I2PAddress,
    I2PTunnelTransport,
    I2PServerTunnelProtocol,
)

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
        if not (hasattr(self.factory, 'tunnelNick') and self.factory.tunnelNick):
            # All tunnels in the same process use the same tunnelNick
            # TODO is using the PID a security risk?
            self.factory.tunnelNick = 'txi2p-%d' % os.getpid()

        used_ports = []
        for i in range(0, len(tunnels)):
            if tunnels[i]['nickname'] == self.factory.tunnelNick:
                # Tunnel already exists, use its settings.
                self.tunnelExists = True
                self.tunnelRunning = tunnels[i]['running']
                self.factory.inhost = tunnels[i]['inhost']
                self.factory.inport = tunnels[i]['inport']
                self.factory.outhost = tunnels[i]['outhost']
                self.factory.outport = tunnels[i]['outport']
                # The tunnel will be removed by the Factory
                # that created it.
                self.factory.removeTunnelWhenFinished = False
                break
            else:
                if tunnels[i]['inport']:
                    used_ports.append(tunnels[i]['inport'])
                if tunnels[i]['outport']:
                    used_ports.append(tunnels[i]['outport'])
        else:
            # This is a new tunnel.
            # Default port offset is at the end of the tunnels list
            offset = 2*(len(tunnels))
            # Find an offset that does not clash
            while (DEFAULT_INPORT + offset) in used_ports or (DEFAULT_OUTPORT + offset) in used_ports:
                offset += 2
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


class I2PClientTunnelProtocol(Protocol):
    def __init__(self, wrappedProto, clientAddr, dest):
        self.wrappedProto = wrappedProto
        self._clientAddr = clientAddr
        self.dest = dest
        self._errmsg = None

    def connectionMade(self):
        # Substitute transport for an I2P wrapper
        self.transport = I2PTunnelTransport(self.transport, self._clientAddr,
                                            I2PAddress(self.dest))
        self.isConnected = False
        # First line sent must be the Destination to connect to.
        self.transport.write(self.dest + '\n')
        self.wrappedProto.makeConnection(self.transport)

    def dataReceived(self, data):
        # Check for a successful connection
        if not self.isConnected:
            if data.startswith("ERROR"):
                self._errmsg = data[6:]
                # I2P connection failed
                self.transport.loseConnection()
                return
            else:
                self.isConnected = True

        # Pass all received data to the wrapped Protocol.
        self.wrappedProto.dataReceived(data)

    def connectionLost(self, reason):
        if self._errmsg:
            if self._errmsg.startswith("Can't find destination"):
                reason = Failure(UnknownHostError(string=self._errmsg))
            else:
                reason = Failure(ConnectError(string=self._errmsg))
        self.factory.i2pConnectionLost(self.wrappedProto, reason)


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
