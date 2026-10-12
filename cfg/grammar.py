"""Modelo de gramática y formato de texto compartido con la etapa de CYK.

Los símbolos se separan con espacios. Los lados izquierdos, el símbolo inicial
y las declaraciones definen no terminales; los demás símbolos son terminales. La cadena vacía
se representa internamente con la tupla (), nunca con la palabra 'e'.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

EPSILON_MARKERS = frozenset({"e", "ε"})


def _valid_symbol(symbol: str) -> bool:
    return bool(symbol) and not any(c.isspace() for c in symbol) and (
        symbol not in EPSILON_MARKERS
        and not any(x in symbol for x in ("|", "->", "#", "%"))
    )


@dataclass(frozen=True, order=True)
class Production:
    lhs: str
    rhs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "rhs", tuple(self.rhs))
        if not _valid_symbol(self.lhs) or any(not _valid_symbol(s) for s in self.rhs):
            raise ValueError("Símbolo inválido en una producción.")


@dataclass(frozen=True)
class Grammar:
    start: str
    productions: frozenset[Production]
    declared_nonterminals: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "productions", frozenset(self.productions))
        object.__setattr__(self, "declared_nonterminals", frozenset(self.declared_nonterminals)
                           | {self.start} | {p.lhs for p in self.productions})
        if not _valid_symbol(self.start):
            raise ValueError("Símbolo inicial inválido.")
        if any(not _valid_symbol(s) for s in self.declared_nonterminals):
            raise ValueError("Declaración de no terminales inválida.")

    @property
    def nonterminals(self) -> frozenset[str]:
        return frozenset({self.start} | {p.lhs for p in self.productions}) | self.declared_nonterminals

    @property
    def terminals(self) -> frozenset[str]:
        return frozenset(s for p in self.productions for s in p.rhs) - self.nonterminals

    def to_text(self) -> str:
        # La cabecera conserva el inicio incluso cuando el lenguaje es vacío.
        lines = [f"%start {self.start}"]
        without_rules = self.nonterminals - {self.start} - {p.lhs for p in self.productions}
        if without_rules:
            lines.append("%nonterminals " + " ".join(sorted(without_rules)))
        for lhs in sorted(self.nonterminals, key=lambda s: (s != self.start, s)):
            alternatives = sorted(p.rhs for p in self.productions if p.lhs == lhs)
            if alternatives:
                body = " | ".join(" ".join(rhs) if rhs else "e" for rhs in alternatives)
                lines.append(f"{lhs} -> {body}")
        return "\n".join(lines) + "\n"


def parse_grammar(text: str, start: str | None = None) -> Grammar:
    """Lee A -> B C | palabra; e/ε solos significan vacío.

Sin %start o argumento explícito, se usa el primer lado izquierdo.
Se aceptan comentarios de línea completa que comiencen con #.
"""
    productions: set[Production] = set()
    declared_start = None
    declared_nonterminals: set[str] = set()
    first_lhs = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("%nonterminals"):
            parts = line.split()
            if len(parts) < 2 or parts[0] != "%nonterminals" or any(
                not _valid_symbol(s) for s in parts[1:]
            ):
                raise ValueError(f"Línea {number}: declaración de no terminales inválida.")
            declared_nonterminals.update(parts[1:])
            continue
        if line.startswith("%start"):
            parts = line.split()
            if len(parts) != 2 or parts[0] != "%start" or declared_start is not None:
                raise ValueError(f"Línea {number}: cabecera %start inválida o repetida.")
            declared_start = parts[1]
            continue
        if line.count("->") != 1:
            raise ValueError(f"Línea {number}: se esperaba una producción con ->.")
        lhs, body = (part.strip() for part in line.split("->"))
        if not _valid_symbol(lhs):
            raise ValueError(f"Línea {number}: lado izquierdo inválido.")
        if first_lhs is None:
            first_lhs = lhs
        for alternative in body.split("|"):
            symbols = tuple(alternative.split())
            if not symbols:
                raise ValueError(f"Línea {number}: use e o ε para la producción vacía.")
            if len(symbols) == 1 and symbols[0] in EPSILON_MARKERS:
                symbols = ()
            elif EPSILON_MARKERS.intersection(symbols):
                raise ValueError(f"Línea {number}: e/ε deben aparecer solos.")
            try:
                productions.add(Production(lhs, symbols))
            except ValueError as exc:
                raise ValueError(f"Línea {number}: {exc}") from exc
    selected = start if start is not None else declared_start or first_lhs
    if selected is None:
        raise ValueError("No hay gramática: falta una producción o cabecera %start.")
    if productions and selected not in {p.lhs for p in productions} | declared_nonterminals | {declared_start}:
        raise ValueError(f"El símbolo inicial {selected!r} no tiene producciones.")
    return Grammar(selected, frozenset(productions), frozenset(declared_nonterminals))


def read_grammar(path: str | Path, start: str | None = None) -> Grammar:
    return parse_grammar(Path(path).read_text(encoding="utf-8-sig"), start=start)
