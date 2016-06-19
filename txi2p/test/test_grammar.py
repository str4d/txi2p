# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from parsley import makeGrammar, ParseError

from txi2p.grammar import bobGrammarSource, samGrammarSource


bobGrammar = makeGrammar(bobGrammarSource, {})
samGrammar = makeGrammar(samGrammarSource, {})

def stringParserFromRule(grammar, rule):
    def parseString(s):
        return getattr(grammar(s), rule)()
    return parseString


class TestBOBGrammar(unittest.TestCase):
    def _test(self, rule, data, expected):
        parse = stringParserFromRule(bobGrammar, rule)
        result = parse(data)
        self.assertEqual(result, expected)

    def test_BOB_clear(self):
        self._test('BOB_clear', 'OK cleared\n', (True, 'cleared'))
        self._test('BOB_clear', 'ERROR tunnel is active\n', (False, 'tunnel is active'))

    def test_BOB_getdest(self):
        self._test('BOB_getdest', 'OK spam\n', (True, 'spam'))

    def test_BOB_getkeys(self):
        self._test('BOB_getkeys', 'OK spameggs\n', (True, 'spameggs'))

    def test_BOB_list(self):
        spam = {
            'nickname': 'spam',
            'starting': False,
            'running': True,
            'stopping': False,
            'keys': True,
            'quiet': False,
            'inport': 12345,
            'inhost': 'localhost',
            'outport': 23456,
            'outhost': 'localhost'
        }
        eggs = {
            'nickname': 'eggs',
            'starting': False,
            'running': False,
            'stopping': False,
            'keys': True,
            'quiet': False,
            'inport': None,
            'inhost': 'localhost',
            'outport': None,
            'outhost': 'localhost'
        }

        self._test('BOB_list', 'OK Listing done\n', (True, 'Listing done', []))
        self._test('BOB_list', 'DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nDATA NICKNAME: eggs STARTING: false RUNNING: false STOPPING: false KEYS: true QUIET: false INPORT: not_set INHOST: localhost OUTPORT: not_set OUTHOST: localhost\nOK Listing done\n', (True, 'Listing done', [spam, eggs]))
        self._test('BOB_list', 'ERROR ni!\n', (False, 'ni!', []))


class TestSAMGrammar(unittest.TestCase):
    def _test(self, rule, data, expected):
        parse = stringParserFromRule(samGrammar, rule)
        result = parse(data)
        self.assertEqual(result, expected)

    def test_SAM_hello(self):
        self._test('SAM_hello', 'HELLO REPLY RESULT=OK VERSION=3.1\n',
                   {'result': 'OK', 'version': '3.1'})
        self._test('SAM_hello', 'HELLO REPLY RESULT=NOVERSION\n', {'result': 'NOVERSION'})
        self._test('SAM_hello',
                   'HELLO REPLY RESULT=I2P_ERROR MESSAGE="Something failed"\n',
                   {'result': 'I2P_ERROR', 'message': 'Something failed'})

    def test_SAM_session_status(self):
        self._test('SAM_session_status',
                   'SESSION STATUS RESULT=OK DESTINATION=privkey\n',
                   {'result': 'OK', 'destination': 'privkey'})
        self._test('SAM_session_status',
                   'SESSION STATUS RESULT=DUPLICATED_ID\n',
                   {'result': 'DUPLICATED_ID'})

    def test_SAM_stream_status(self):
        self._test('SAM_stream_status', 'STREAM STATUS RESULT=OK\n', {'result': 'OK'})
        self._test('SAM_stream_status',
                   'STREAM STATUS RESULT=CANT_REACH_PEER MESSAGE="Can\'t reach peer"\n',
                   {'result': 'CANT_REACH_PEER', 'message': 'Can\'t reach peer'})

    def test_SAM_naming_reply(self):
        self._test('SAM_naming_reply',
                   'NAMING REPLY RESULT=OK NAME=name VALUE=dest\n',
                   {'result': 'OK', 'name': 'name', 'value': 'dest'})
        self._test('SAM_naming_reply',
                   'NAMING REPLY RESULT=KEY_NOT_FOUND\n',
                   {'result': 'KEY_NOT_FOUND'})

    def test_SAM_dest_reply(self):
        self._test('SAM_dest_reply',
                   'DEST REPLY PUB=foo PRIV=foobar\n',
                   {'pub': 'foo', 'priv': 'foobar'})

    def test_SAM_ping(self):
        self._test('SAM_ping', 'PING\n', None)
        self._test('SAM_ping', 'PING 1234567890\n', '1234567890')

    def test_SAM_pong(self):
        self._test('SAM_pong', 'PONG\n', None)
        self._test('SAM_pong', 'PONG 1234567890\n', '1234567890')
