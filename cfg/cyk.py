"""Reconocimiento CYK mediante intervalos semiabiertos [i, j)."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from .cnf import validate_cnf
from .grammar import Grammar, Production


@dataclass(frozen=True)
class _Backpointer:
    production: Production
    split: int | None = None


@dataclass(frozen=True)
class ParseTree:
    """Nodo de una regla CNF; los terminales se guardan como cadenas hijas."""
    production: Production
    children: tuple[ParseTree | str, ...] = ()

    def leaves(self) -> tuple[str, ...]:
        result = []
        pending: list[ParseTree | str] = [self]
        while pending:
            node = pending.pop()
            if isinstance(node, str):
                result.append(node)
            else:
                pending.extend(reversed(node.children))
        return tuple(result)

    def to_text(self) -> str:
        """Árbol indentado, incluida una hoja ε para la producción vacía."""
        lines = []
        pending: list[tuple[ParseTree | str, int]] = [(self, 0)]
        while pending:
            node, depth = pending.pop()
            if isinstance(node, str):
                lines.append("  " * depth + node)
            else:
                lines.append("  " * depth + node.production.lhs)
                if not node.production.rhs:
                    lines.append("  " * (depth + 1) + "ε")
                pending.extend((child, depth + 1) for child in reversed(node.children))
        return "\n".join(lines)


@dataclass(frozen=True)
class CYKResult:
    accepted: bool
    tokens: tuple[str, ...]
    elapsed_seconds: float
    tree: ParseTree | None


def _build_tree(chart, start: str, size: int) -> ParseTree:
    # Postorden iterativo: evita depender del límite de recursión de Python.
    root = (0, size, start)
    pending = [(root, False)]
    built: dict[tuple[int, int, str], ParseTree] = {}
    while pending:
        key, ready = pending.pop()
        i, j, symbol = key
        pointer = chart[i, j][symbol]
        rule, split = pointer.production, pointer.split
        if split is None:
            built[key] = ParseTree(rule, rule.rhs)
            continue
        left = (i, split, rule.rhs[0])
        right = (split, j, rule.rhs[1])
        if ready:
            built[key] = ParseTree(rule, (built[left], built[right]))
        else:
            pending.extend(((key, True), (right, False), (left, False)))
    return built[root]


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


def cyk(grammar: Grammar, tokens: Iterable[str]) -> CYKResult:
    """Reconoce tokens exactos y devuelve un árbol de la CNF si son aceptados.

    Cronometra índices, tabla y decisión; excluye validación de CNF, preparación
    de tokens y reconstrucción del árbol. No convierte ni normaliza la entrada.
    """
    errors = validate_cnf(grammar)
    if errors:
        raise ValueError("CYK requiere una gramática en CNF: " + "; ".join(errors))
    if isinstance(tokens, str):
        raise TypeError("CYK recibe tokens, no una frase; use frase.split().")
    word = tuple(tokens)
    if any(not isinstance(token, str) or not token or any(c.isspace() for c in token)
           for token in word):
        raise ValueError("Cada token debe ser un símbolo completo sin espacios.")
    started = perf_counter()
    chart = _recognize(grammar, word)
    accepted = grammar.start in chart[0, len(word)]
    elapsed = perf_counter() - started
    tree = _build_tree(chart, grammar.start, len(word)) if accepted else None
    return CYKResult(accepted, word, elapsed, tree)
