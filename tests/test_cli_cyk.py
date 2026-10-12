"""Integración de conversión, normalización y reconocimiento por consola."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

from cfg import read_grammar, validate_cnf

ROOT = Path(__file__).resolve().parents[1]


class RecognitionCliTests(unittest.TestCase):
    def run_cli(self, *args, input=None):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), *map(str, args)],
            input=input, capture_output=True, encoding="utf-8", cwd=ROOT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def test_normalization_and_tree(self):
        result = self.run_cli("data/ingles.txt", "--sentence", "  She\tEATS a cake with a fork  ")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("SÍ\n"))
        self.assertRegex(result.stdout, r"Tiempo de reconocimiento: \d+\.\d+ s")
        self.assertIn("Árbol sintáctico (CNF):\nS\n", result.stdout)

    def test_rejections_and_case_sensitive(self):
        for phrase, extra in (("", ()), ("she dances", ()), ("she eats.", ()),
                              ("She eats", ("--case-sensitive",))):
            with self.subTest(phrase=phrase):
                result = self.run_cli("data/ingles.txt", "--sentence", phrase, *extra)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.startswith("NO\n"))
                self.assertNotIn("Árbol", result.stdout)

    def test_stdin_and_arithmetic(self):
        result = self.run_cli("data/ingles.txt", "--stdin", input="He cooks\n")
        self.assertTrue(result.stdout.startswith("SÍ\n"), result.stderr)
        result = self.run_cli("data/1.txt", "--sentence", "( id ) + id")
        self.assertTrue(result.stdout.startswith("SÍ\n"), result.stderr)

    def test_recognition_with_export_trace_and_custom_start(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            source = path / "source.txt"
            source.write_text("Unused -> no\nRoot -> A B\nA -> yes\nB -> please\n", encoding="utf-8")
            result = self.run_cli(source, "--start", "Root", "--sentence", "yes please",
                                  "--output", path / "cnf.txt", "--trace-dir", path / "stages")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith("SÍ\n"))
            self.assertIn("\nRoot\n", result.stdout)
            self.assertEqual(validate_cnf(read_grammar(path / "cnf.txt")), ())
            self.assertEqual(len(list((path / "stages").glob("*.txt"))), 7)

    def test_sentence_and_stdin_are_exclusive(self):
        result = self.run_cli("data/ingles.txt", "--sentence", "he cooks", "--stdin")
        self.assertEqual(result.returncode, 2)
