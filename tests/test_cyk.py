"""Pruebas de reconocimiento y reconstrucción de la segunda mitad."""

from pathlib import Path
from itertools import product
import random
import unittest

from cfg import Grammar, ParseTree, Production, convert_to_cnf, parse_grammar, read_grammar
from cfg.cyk import cyk
from test_conversion import bounded_language

ROOT = Path(__file__).resolve().parents[1]


class RecognitionTests(unittest.TestCase):
    def assert_valid_tree(self, grammar, tokens, tree):
        self.assertIsInstance(tree, ParseTree)
        self.assertEqual(tree.production.lhs, grammar.start)
        self.assertEqual(tree.leaves(), tuple(tokens))
        pending = [tree]
        while pending:
            node = pending.pop()
            self.assertIn(node.production, grammar.productions)
            self.assertEqual(tuple(child.production.lhs if isinstance(child, ParseTree) else child
                                   for child in node.children), node.production.rhs)
            pending.extend(child for child in node.children if isinstance(child, ParseTree))

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
                result = cyk(grammar, phrase.split())
                self.assertEqual(result.accepted, expected)
                self.assertGreaterEqual(result.elapsed_seconds, 0)
                if expected:
                    self.assert_valid_tree(grammar, phrase.split(), result.tree)
                else:
                    self.assertIsNone(result.tree)

    def test_empty_languages_and_nonstandard_start(self):
        for source, empty, single in (("%start Root", False, False),
                                      ("Root -> e", True, False),
                                      ("Root -> e | id", True, True)):
            grammar = parse_grammar(source)
            self.assertEqual(cyk(grammar, []).accepted, empty)
            self.assertEqual(cyk(grammar, ["id"]).accepted, single)
            if empty:
                tree = cyk(grammar, []).tree
                self.assertEqual(tree.leaves(), ())
                self.assertEqual(tree.to_text(), "Root\n  ε")

    def test_conversion_and_multi_character_tokens(self):
        grammar = convert_to_cnf(read_grammar(ROOT / "data/1.txt")).grammar
        self.assertTrue(cyk(grammar, ["(", "id", ")", "+", "id"]).accepted)
        self.assertFalse(cyk(grammar, ["id", "+"]).accepted)

    def test_invalid_cnf_and_token_input(self):
        with self.assertRaises(ValueError):
            cyk(parse_grammar("S -> A\nA -> a"), ["a"])
        grammar = parse_grammar("Root -> id")
        with self.assertRaises(TypeError):
            cyk(grammar, "id")
        for tokens in ([""], ["two words"], [None]):
            with self.subTest(tokens=tokens), self.assertRaises(ValueError):
                cyk(grammar, tokens)

    def test_ambiguous_grammar_returns_one_valid_deterministic_tree(self):
        grammar = parse_grammar("Root -> A A\nA -> A A | a")
        first = cyk(grammar, ["a"] * 5)
        self.assertTrue(first.accepted)
        self.assert_valid_tree(grammar, ["a"] * 5, first.tree)
        self.assertEqual(cyk(grammar, ["a"] * 5).tree, first.tree)

    def test_both_extreme_splits_and_repeated_symbols(self):
        for body in ("A Tail", "Head A"):
            grammar = parse_grammar(f"Root -> {body}\nTail -> B C\nHead -> A B\nA -> a\nB -> b\nC -> c")
            tokens = ["a", "b", "c"] if body == "A Tail" else ["a", "b", "a"]
            result = cyk(grammar, tokens)
            self.assertTrue(result.accepted)
            self.assert_valid_tree(grammar, tokens, result.tree)
        grammar = parse_grammar("Root -> A A\nA -> a")
        self.assertTrue(cyk(grammar, ["a", "a"]).accepted)

    def test_seeded_grammars_against_independent_oracle(self):
        rng = random.Random(2026)
        bodies = [(), ("a",), ("b",), ("S",), ("A",), ("B",),
                  ("A", "B"), ("S", "A"), ("a", "B"), ("A", "A", "B")]
        words = [word for size in range(4) for word in product(("a", "b"), repeat=size)]
        for case in range(40):
            original = Grammar("S", frozenset(
                Production(lhs, rhs) for lhs in ("S", "A", "B")
                for rhs in rng.sample(bodies, rng.randint(1, 4))
            ))
            expected = bounded_language(original, 3)
            grammar = convert_to_cnf(original).grammar
            for word in words:
                with self.subTest(case=case, word=word):
                    result = cyk(grammar, word)
                    self.assertEqual(result.accepted, word in expected)
                    if result.accepted:
                        self.assert_valid_tree(grammar, word, result.tree)
                    else:
                        self.assertIsNone(result.tree)

    def test_arithmetic_language_and_trees_against_oracle(self):
        original = read_grammar(ROOT / "data/1.txt")
        reference = read_grammar(ROOT / "data/1-cnf.txt")
        expected = bounded_language(original, 5)
        self.assertEqual(expected, bounded_language(reference, 5))
        grammar = convert_to_cnf(original).grammar
        for word in sorted(expected):
            with self.subTest(word=word):
                result = cyk(grammar, word)
                self.assertTrue(result.accepted)
                self.assert_valid_tree(grammar, word, result.tree)

    def test_generator_and_exact_case_tokens(self):
        grammar = parse_grammar("Root -> ID")
        result = cyk(grammar, (token for token in ["ID"]))
        self.assertTrue(result.accepted)
        self.assertEqual(result.tokens, ("ID",))
        self.assertFalse(cyk(grammar, ["id"]).accepted)
