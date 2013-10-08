# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

import unittest

from parsley import makeGrammar, ParseError

from i2p.twisted.grammar import bobGrammarSource


bobGrammar = makeGrammar(bobGrammarSource, {})

def stringParserFromRule(grammar, rule):
    def parseString(s):
        return getattr(grammar(s), rule)()
    return parseString


class TestBOBGrammar(unittest.TestCase):
    def test_BOB_clear(self):
        parse = stringParserFromRule(bobGrammar, 'BOB_clear')
        self.assertEqual(parse('OK cleared\n'), (True, 'cleared'))
        self.assertEqual(parse('ERROR tunnel is active\n'), (False, 'tunnel is active'))

    def test_BOB_getdest(self):
        parse = stringParserFromRule(bobGrammar, 'BOB_getdest')
        self.assertEqual(parse('OK spam\n'), (True, 'spam'))

    def test_BOB_getkeys(self):
        parse = stringParserFromRule(bobGrammar, 'BOB_getkeys')
        self.assertEqual(parse('OK spameggs\n'), (True, 'spameggs'))

    def test_BOB_list(self):
        parse = stringParserFromRule(bobGrammar, 'BOB_list')
        self.assertEqual(parse('OK Listing done\n'), (True, 'Listing done', []))
        self.assertEqual(parse('DATA spam\nDATA eggs\nOK Listing done\n'), (True, 'Listing done', ['spam', 'eggs']))
        self.assertEqual(parse('ERROR ni!\n'), (False, 'ni!', []))
