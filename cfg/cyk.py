"""Reconocimiento CYK mediante intervalos semiabiertos [i, j)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .cnf import validate_cnf
from .grammar import Grammar, Production


@dataclass(frozen=True)
class _Backpointer:
    production: Production
    split: int | None = None


def _recognize(grammar: Grammar, tokens: tuple[str, ...]):
    """Cada celda guarda una derivación por no terminal, sin enumerar ambigüedad."""
    lexical: dict[str, list[Production]] = {}
    binary: dict[tuple[str, ...], list[Production]] = {}
    for rule in sorted(grammar.productions):
        if len(rule.rhs) == 1:
            lexical.setdefault(rule.rhs[0], []).append(rule)
        elif len(rule.rhs) == 2:
            binary.setdefault(rule.rhs, []).append(rule)

    chart: dict[tuple[int, int], dict[str, _Backpointer]] = {}
    for i, token in enumerate(tokens):
        chart[i, i + 1] = {
            rule.lhs: _Backpointer(rule) for rule in lexical.get(token, ())
        }
    for length in range(2, len(tokens) + 1):
        for i in range(len(tokens) - length + 1):
            j = i + length
            cell: dict[str, _Backpointer] = {}
            for split in range(i + 1, j):
                for left in sorted(chart[i, split]):
                    for right in sorted(chart[split, j]):
                        for rule in binary.get((left, right), ()):
                            cell.setdefault(rule.lhs, _Backpointer(rule, split))
            chart[i, j] = cell
    if not tokens:
        empty = Production(grammar.start, ())
        chart[0, 0] = {grammar.start: _Backpointer(empty)} if empty in grammar.productions else {}
    return chart


def cyk(grammar: Grammar, tokens: Iterable[str]) -> bool:
    """Reconoce tokens completos en CNF estricta; no normaliza sus símbolos."""
    errors = validate_cnf(grammar)
    if errors:
        raise ValueError("CYK requiere una gramática en CNF: " + "; ".join(errors))
    if isinstance(tokens, str):
        raise TypeError("CYK recibe tokens, no una frase; use frase.split().")
    word = tuple(tokens)
    if any(not isinstance(token, str) or not token or any(c.isspace() for c in token)
           for token in word):
        raise ValueError("Cada token debe ser un símbolo completo sin espacios.")
    chart = _recognize(grammar, word)
    return grammar.start in chart[0, len(word)]
