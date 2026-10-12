"""Pruebas de reconocimiento y reconstrucción de la segunda mitad."""

from pathlib import Path
import unittest

from cfg import convert_to_cnf, parse_grammar, read_grammar
from cfg.cyk import cyk

ROOT = Path(__file__).resolve().parents[1]


class RecognitionTests(unittest.TestCase):
    def test_english_examples(self):
        grammar = read_grammar(ROOT / "data/ingles.txt")
        examples = {
            "she eats a cake with a fork": True,
            "the cat drinks the beer": True,
            "he cooks": True,
            "she eats": True,
            "the cake drinks a knife": True,
            "she eats cake": False,
            "cat drinks the beer": False,
            "she dances": False,
            "": False,
        }
        for phrase, expected in examples.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(cyk(grammar, phrase.split()), expected)

    def test_empty_languages_and_nonstandard_start(self):
        for source, empty, single in (("%start Root", False, False),
                                      ("Root -> e", True, False),
                                      ("Root -> e | id", True, True)):
            grammar = parse_grammar(source)
            self.assertEqual(cyk(grammar, []), empty)
            self.assertEqual(cyk(grammar, ["id"]), single)

    def test_conversion_and_multi_character_tokens(self):
        grammar = convert_to_cnf(read_grammar(ROOT / "data/1.txt")).grammar
        self.assertTrue(cyk(grammar, ["(", "id", ")", "+", "id"]))
        self.assertFalse(cyk(grammar, ["id", "+"]))

    def test_invalid_cnf_and_token_input(self):
        with self.assertRaises(ValueError):
            cyk(parse_grammar("S -> A\nA -> a"), ["a"])
        grammar = parse_grammar("Root -> id")
        with self.assertRaises(TypeError):
            cyk(grammar, "id")
        for tokens in ([""], ["two words"], [None]):
            with self.subTest(tokens=tokens), self.assertRaises(ValueError):
                cyk(grammar, tokens)
