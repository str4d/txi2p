try:
    from txi2p._version import __version__, __revision__
except ImportError:
    __version__ = __revision__ = None

from txi2p.address import I2PAddress
from txi2p.utils import generateDestination, testAPI
