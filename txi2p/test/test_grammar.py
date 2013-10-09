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
        self._test('BOB_list', 'OK Listing done\n', (True, 'Listing done', []))
        self._test('BOB_list', 'DATA spam\nDATA eggs\nOK Listing done\n', (True, 'Listing done', ['spam', 'eggs']))
        self._test('BOB_list', 'ERROR ni!\n', (False, 'ni!', []))
