# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from parsley import makeGrammar, ParseError

from txi2p.grammar import bobGrammarSource


bobGrammar = makeGrammar(bobGrammarSource, {})

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
            'inport': '12345',
            'inhost': 'localhost',
            'outport': '23456',
            'outhost': 'localhost'
        }
        eggs = {
            'nickname': 'eggs',
            'starting': False,
            'running': False,
            'stopping': False,
            'keys': True,
            'quiet': False,
            'inport': 'not_set',
            'inhost': 'localhost',
            'outport': 'not_set',
            'outhost': 'localhost'
        }

        self._test('BOB_list', 'OK Listing done\n', (True, 'Listing done', []))
        self._test('BOB_list', 'DATA NICKNAME: spam STARTING: false RUNNING: true STOPPING: false KEYS: true QUIET: false INPORT: 12345 INHOST: localhost OUTPORT: 23456 OUTHOST: localhost\nDATA NICKNAME: eggs STARTING: false RUNNING: false STOPPING: false KEYS: true QUIET: false INPORT: not_set INHOST: localhost OUTPORT: not_set OUTHOST: localhost\nOK Listing done\n', (True, 'Listing done', [spam, eggs]))
        self._test('BOB_list', 'ERROR ni!\n', (False, 'ni!', []))
