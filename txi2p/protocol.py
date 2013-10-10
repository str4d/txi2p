# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from parsley import makeProtocol

from txi2p import grammar


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
        self.transport.write('\n')

    def sendStatus(self, tunnelNick):
        self.transport.write('status %s\n' % tunnelNick)

    def sendStop(self):
        self.transport.write('stop\n')

    def sendVerify(self, key):
        self.transport.write('verify %s\n' % key)

    def sendVisit(self):
        self.transport.write('visit\n')


class BOBReceiver(object):
    currentRule = ''

    def __init__(self, sender):
        self.sender = sender

    def prepareParsing(self, parser):
        pass

    def finishParsing(self, reason):
        pass

    def clear(self, success, info):
        if success:
            # Do something
        else: # Try again. TODO: Limit retries
            self.sender.sendClear()

    def getdest(self, success, info):
        if success:
            # Do something

    def getkeys(self, success, info):
        if success:
            # Do something

    def getnick(self, success, info):
        if success:
            # Do something

    def inhost(self, success, info):
        if success:
            # Do something

    def inport(self, success, info):
        if success:
            # Do something

    def list(self, success, info, data):
        if success:
            # Do something

    def newkeys(self, success, info):
        if success:
            # Do something

    def option(self, success, info):
        if success:
            # Do something

    def outhost(self, success, info):
        if success:
            # Do something

    def outport(self, success, info):
        if success:
            # Do something

    def quiet(self, success, info):
        if success:
            # Do something

    def quit(self, success, info):
        # Do something

    def setkeys(self, success, info):
        if success:
            # Do something

    def setnick(self, success, info):
        if success:
            # Do something

    def show(self, success, info):
        if success:
            # Do something

    def showprops(self, success, info):
        if success:
            # Do something

    def start(self, success, info):
        if success:
            # Do something

    def status(self, success, info):
        if success:
            # Do something

    def stop(self, success, info):
        if success:
            # Do something

    def verify(self, success, info):
        if success:
            # Do something

    def visit(self, success, info):
        # Do something


# A Protocol for making an I2P client tunnel via BOB
I2PClientTunnelCreatorBOBClient = makeProtocol(
    grammar.i2pTunnelBOBGrammarSource,
    BOBSender,
    I2PClientTunnelCreatorBOBReceiver)

# A Protocol for making an I2P server tunnel via BOB
I2PServerTunnelCreatorBOBClient = makeProtocol(
    grammar.i2pTunnelBOBGrammarSource,
    BOBSender,
    I2PServerTunnelCreatorBOBReceiver)
