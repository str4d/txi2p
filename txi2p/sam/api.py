from txi2p.sam.session import DestGenerateFactory


def generateDestination(keyfile, samEndpoint):
    destFac = DestGenerateFactory(keyfile)
    d = samEndpoint.connect(destFac)
    d.addCallback(lambda proto: destFac.deferred)
    return d
