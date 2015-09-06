# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet.error import (
    ConnectBindError,
    ConnectError,
    NoRouteError,
    TCPTimedOutError,
    UnknownHostError,
)


RESULT_OK = 'OK'
RESULT_CANT_REACH_PEER = 'CANT_REACH_PEER'
RESULT_DUPLICATED_DEST = 'DUPLICATED_DEST'
RESULT_I2P_ERROR = 'I2P_ERROR'
RESULT_INVALID_KEY = 'INVALID_KEY'
RESULT_KEY_NOT_FOUND = 'KEY_NOT_FOUND'
RESULT_PEER_NOT_FOUND = 'PEER_NOT_FOUND'
RESULT_TIMEOUT = 'TIMEOUT'

samErrorMap = {
    RESULT_CANT_REACH_PEER: NoRouteError,
    RESULT_DUPLICATED_DEST: ConnectBindError,
    RESULT_I2P_ERROR: ConnectError,
    RESULT_INVALID_KEY: ConnectError,
    RESULT_KEY_NOT_FOUND: UnknownHostError,
    RESULT_PEER_NOT_FOUND: NoRouteError,
    RESULT_TIMEOUT: TCPTimedOutError,
}
