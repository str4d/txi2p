try:
    from txi2p._version import __version__, __version_tuple__
except ImportError:
    __version__ = __version_tuple__ = None

from txi2p.address import I2PAddress
from txi2p.utils import generateDestination, testAPI
