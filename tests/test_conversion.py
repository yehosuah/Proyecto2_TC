"""Pruebas de la primera etapa; no implementan el algoritmo CYK."""

from itertools import product
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from cfg import Grammar, Production, convert_to_cnf, parse_grammar, read_grammar, validate_cnf

ROOT = Path(__file__).resolve().parents[1]


def bounded_language(grammar, maximum):
    """Oráculo independiente: punto fijo de palabras de longitud <= maximum.

No limita pasos de derivación: termina cuando deja de descubrir palabras.
Solo se usa con gramáticas pequeñas; no es un reconocedor para la aplicación.
"""
    words = {nt: set() for nt in grammar.nonterminals}
    changed = True
    while changed:
        changed = False
        for p in sorted(grammar.productions):
            choices = [tuple(words[s]) if s in words else ((s,),) for s in p.rhs]
            for pieces in product(*choices):
                word = tuple(s for piece in pieces for s in piece)
                if len(word) <= maximum and word not in words[p.lhs]:
                    words[p.lhs].add(word)
                    changed = True
    return words[grammar.start]


class ParsingTests(unittest.TestCase):
    def test_original_tokens_and_epsilon(self):
        grammar = read_grammar(ROOT / "data/1.txt")
        self.assertEqual(grammar.start, "E")
        self.assertIn(Production("F", ("id",)), grammar.productions)
        self.assertIn(Production("X", ()), grammar.productions)
        self.assertNotIn("e", grammar.terminals)

    def test_comments_duplicates_unicode_and_explicit_start(self):
        grammar = parse_grammar("# prueba\nA -> id | id\nS -> A | ε", start="S")
        self.assertEqual(len(grammar.productions), 3)
        self.assertEqual(parse_grammar(grammar.to_text()), grammar)

    def test_empty_language_serialization(self):
        grammar = Grammar("S", frozenset())
        self.assertEqual(parse_grammar(grammar.to_text()), grammar)

    def test_nonterminal_without_rules_stays_nonterminal(self):
        grammar = parse_grammar("%nonterminals A\nS -> A x")
        self.assertEqual(grammar.terminals, {"x"})
        self.assertEqual(parse_grammar(grammar.to_text()), grammar)
        self.assertEqual(convert_to_cnf(grammar).grammar.productions, frozenset())

    def test_invalid_inputs(self):
        for source in ("", "A => a", "A B -> a", "S ->", "S -> a |",
                       "S -> e a", "S -> a -> b", "%start S\n%start A\nS -> a",
                       "%nonterminals\nS -> a", "S -> #a", "%start e"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_grammar(source)
        with self.assertRaises(ValueError):
            parse_grammar("S -> a", start="Typo")


class ConversionTests(unittest.TestCase):
    def assert_preserves(self, source, maximum=4, expected=None):
        original = parse_grammar(source)
        result = convert_to_cnf(original)
        language = bounded_language(original, maximum)
        if expected is not None:
            self.assertEqual(language, expected)
        for name, stage in result.stages:
            with self.subTest(stage=name):
                self.assertEqual(bounded_language(stage, maximum), language)
                self.assertEqual(parse_grammar(stage.to_text()), stage)
        self.assertEqual(validate_cnf(result.grammar), ())
        self.assertEqual(convert_to_cnf(result.grammar).grammar, result.grammar)
        return result

    def test_nullable_repeated_symbols(self):
        self.assert_preserves("S -> A A\nA -> a | e", expected={(), ("a",), ("a", "a")})

    def test_nullable_start_reused_on_rhs(self):
        self.assert_preserves("S -> A S | e\nA -> a",
                              expected={tuple("a" * n) for n in range(5)})

    def test_epsilon_only_symbol_must_not_become_a_terminal(self):
        self.assert_preserves("S -> A b\nA -> e", expected={("b",)})

    def test_unit_cycles(self):
        self.assert_preserves("S -> A\nA -> B | a\nB -> A | b",
                              expected={("a",), ("b",)})

    def test_unproductive_unit_cycles_must_not_become_terminals(self):
        self.assert_preserves("S -> A x | ok\nA -> B\nB -> A", expected={("ok",)})

    def test_useless_and_unreachable_symbols(self):
        result = self.assert_preserves("S -> A B | a\nA -> a\nB -> B B\nU -> u",
                                       expected={("a",)})
        self.assertEqual(result.grammar.nonterminals, {"S"})

    def test_empty_and_epsilon_only_languages(self):
        self.assert_preserves("S -> A\nA -> S", expected=set())
        self.assert_preserves("S -> e", expected={()})

    def test_mixed_terminals_long_rules_and_name_collisions(self):
        self.assert_preserves("S -> S0 T0 B0 a b\nS0 -> x\nT0 -> y\nB0 -> z", 5,
                              expected={("x", "y", "z", "a", "b")})
        self.assert_preserves("S -> S a | S0 | T0 | B0", 3)

    def test_arithmetic_reference(self):
        original = read_grammar(ROOT / "data/1.txt")
        expected = read_grammar(ROOT / "data/1-cnf.txt")
        result = self.assert_preserves(original.to_text(), 5)
        self.assertEqual(bounded_language(result.grammar, 5), bounded_language(expected, 5))
        self.assertIn(("(", "id", ")", "+", "id"), bounded_language(expected, 5))

    def test_english_already_in_cnf(self):
        grammar = read_grammar(ROOT / "data/ingles.txt")
        self.assertEqual(validate_cnf(grammar), ())
        self.assertEqual(convert_to_cnf(grammar).grammar, grammar)
        self.assertEqual(len(grammar.productions), 30)

    def test_validator_rejects_invalid_shapes(self):
        for source in ("S -> A\nA -> a", "S -> a B\nB -> b", "S -> A B C\nA -> a\nB -> b\nC -> c",
                       "S -> A B\nA -> e\nB -> b", "S -> S A | a\nA -> a"):
            with self.subTest(source=source):
                self.assertTrue(validate_cnf(parse_grammar(source)))

    def test_seeded_small_grammars(self):
        rng = random.Random(2024)
        bodies = [(), ("a",), ("b",), ("S",), ("A",), ("B",), ("A", "B"),
                  ("S", "A"), ("a", "B"), ("A", "A", "B")]
        for case in range(40):
            productions = {Production(lhs, rhs) for lhs in ("S", "A", "B")
                           for rhs in rng.sample(bodies, rng.randint(1, 4))}
            grammar = Grammar("S", frozenset(productions))
            with self.subTest(case=case):
                self.assert_preserves(grammar.to_text(), 3)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "main.py"), *map(str, args)],
                              capture_output=True, text=True, cwd=ROOT)

    def test_export_and_trace_can_be_read_back(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "grammar.txt"
            trace = Path(folder) / "stages"
            completed = self.run_cli(ROOT / "data/1.txt", "--output", destination, "--trace-dir", trace)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(validate_cnf(read_grammar(destination)), ())
            self.assertEqual(len(list(trace.glob("*.txt"))), 7)
            for path in trace.glob("*.txt"):
                read_grammar(path)

    def test_stdout_and_missing_file(self):
        completed = self.run_cli(ROOT / "data/ingles.txt")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(read_grammar(ROOT / "data/ingles.txt"), parse_grammar(completed.stdout))
        completed = self.run_cli(ROOT / "data/not-present.txt")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("Error:", completed.stderr)

    def test_does_not_overwrite_input_or_collide_with_trace(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "00_original.txt"
            source.write_text("S -> a\n", encoding="utf-8")
            for args in (("--output", source), ("--trace-dir", folder)):
                completed = self.run_cli(source, *args)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(source.read_text(), "S -> a\n")


if __name__ == "__main__":
    unittest.main()
