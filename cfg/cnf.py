"""Transformaciones de CFG que conservan su lenguaje, incluida la cadena vacía."""

from __future__ import annotations

from dataclasses import dataclass

from .grammar import Grammar, Production


@dataclass(frozen=True)
class ConversionResult:
    grammar: Grammar
    stages: tuple[tuple[str, Grammar], ...]


class _FreshNames:
    def __init__(self, grammar: Grammar):
        self.used = set(grammar.nonterminals | grammar.terminals)
        self.next_index: dict[str, int] = {}

    def new(self, prefix: str) -> str:
        index = self.next_index.get(prefix, 0)
        while f"{prefix}{index}" in self.used:
            index += 1
        name = f"{prefix}{index}"
        self.used.add(name)
        self.next_index[prefix] = index + 1
        return name


def nullable_symbols(grammar: Grammar) -> frozenset[str]:
    """Punto fijo: A es anulable si todos los símbolos de algún cuerpo lo son."""
    nullable: set[str] = set()
    while True:
        expanded = nullable | {
            p.lhs for p in grammar.productions if all(s in nullable for s in p.rhs)
        }
        if expanded == nullable:
            return frozenset(nullable)
        nullable = expanded


def isolate_start(grammar: Grammar) -> Grammar:
    """Aísla el inicio si aparece a la derecha; permite conservar S -> ε."""
    if not any(
        grammar.start in p.rhs for p in grammar.productions
    ):
        return grammar
    start = _FreshNames(grammar).new("S")
    return Grammar(start, grammar.productions | {Production(start, (grammar.start,))}, grammar.nonterminals)


def eliminate_epsilon(grammar: Grammar) -> Grammar:
    nullable = nullable_symbols(grammar)
    result: set[Production] = set()
    for production in sorted(grammar.productions):
        # Cada ocurrencia anulable ofrece dos opciones: conservarla u omitirla.
        variants: set[tuple[str, ...]] = {()}
        for symbol in production.rhs:
            extended = {rhs + (symbol,) for rhs in variants}
            variants = extended | variants if symbol in nullable else extended
        for rhs in variants:
            if rhs or production.lhs == grammar.start:
                result.add(Production(production.lhs, rhs))
    return Grammar(grammar.start, frozenset(result), grammar.nonterminals)


def eliminate_unit(grammar: Grammar) -> Grammar:
    nonterminals = grammar.nonterminals
    units = {a: set() for a in nonterminals}
    bodies: dict[str, set[tuple[str, ...]]] = {a: set() for a in nonterminals}
    for p in grammar.productions:
        if len(p.rhs) == 1 and p.rhs[0] in nonterminals:
            units[p.lhs].add(p.rhs[0])
        else:
            bodies[p.lhs].add(p.rhs)
    result = set()
    for lhs in sorted(nonterminals):
        reachable = {lhs}
        pending = [lhs]
        while pending:
            for target in sorted(units[pending.pop()] - reachable):
                reachable.add(target)
                pending.append(target)
        for target in reachable:
            result.update(Production(lhs, rhs) for rhs in bodies[target])
    return Grammar(grammar.start, frozenset(result), grammar.nonterminals)


def eliminate_useless(grammar: Grammar) -> Grammar:
    # Primero productividad; después alcance sobre la gramática ya filtrada.
    productive: set[str] = set(grammar.terminals)
    while True:
        expanded = productive | {
            p.lhs for p in grammar.productions if all(s in productive for s in p.rhs)
        }
        if expanded == productive:
            break
        productive = expanded
    remaining = {
        p for p in grammar.productions
        if p.lhs in productive and all(s in productive for s in p.rhs)
    }
    reachable = {grammar.start}
    while True:
        expanded = reachable | {s for p in remaining if p.lhs in reachable for s in p.rhs}
        if expanded == reachable:
            break
        reachable = expanded
    return Grammar(grammar.start, frozenset(p for p in remaining if p.lhs in reachable))


def lift_terminals(grammar: Grammar) -> Grammar:
    names = _FreshNames(grammar)
    nonterminals = grammar.nonterminals
    aliases: dict[str, str] = {}
    result = set()
    for p in sorted(grammar.productions):
        if len(p.rhs) < 2:
            result.add(p)
            continue
        rhs = []
        for symbol in p.rhs:
            if symbol in nonterminals:
                rhs.append(symbol)
            else:
                if symbol not in aliases:
                    aliases[symbol] = names.new("T")
                    result.add(Production(aliases[symbol], (symbol,)))
                rhs.append(aliases[symbol])
        result.add(Production(p.lhs, tuple(rhs)))
    return Grammar(grammar.start, frozenset(result), grammar.nonterminals)


def binarize(grammar: Grammar) -> Grammar:
    names = _FreshNames(grammar)
    result = set()
    for p in sorted(grammar.productions):
        lhs = p.lhs
        for symbol in p.rhs[:-2]:
            auxiliary = names.new("B")
            result.add(Production(lhs, (symbol, auxiliary)))
            lhs = auxiliary
        result.add(Production(lhs, p.rhs[-2:]))
    return Grammar(grammar.start, frozenset(result), grammar.nonterminals)


def validate_cnf(grammar: Grammar) -> tuple[str, ...]:
    """CNF estricta: A -> B C, A -> terminal y, opcionalmente, S -> ε.

El inicio nunca aparece a la derecha. Un inicio sin reglas representa ∅.
Devuelve una tupla vacía cuando no hay errores.
"""
    errors = []
    nonterminals = grammar.nonterminals
    for p in sorted(grammar.productions):
        if grammar.start in p.rhs:
            errors.append(f"El inicio aparece en el lado derecho de {p!r}.")
        valid = (
            (not p.rhs and p.lhs == grammar.start)
            or (len(p.rhs) == 1 and p.rhs[0] not in nonterminals)
            or (len(p.rhs) == 2 and all(s in nonterminals for s in p.rhs))
        )
        if not valid:
            errors.append(f"Producción fuera de CNF: {p!r}.")
    return tuple(errors)


def convert_to_cnf(grammar: Grammar) -> ConversionResult:
    """API pública: devuelve la gramática final y las instantáneas del proceso."""
    stages = [("00_original", grammar)]
    for name, transform in (
        ("01_inicio_protegido", isolate_start),
        ("02_sin_epsilon", eliminate_epsilon),
        ("03_sin_unitarias", eliminate_unit),
        ("04_sin_inutiles", eliminate_useless),
        ("05_terminales_separados", lift_terminals),
        ("06_chomsky", binarize),
    ):
        grammar = transform(grammar)
        stages.append((name, grammar))
    errors = validate_cnf(grammar)
    if errors:
        raise ValueError("La conversión produjo una gramática inválida: " + "; ".join(errors))
    return ConversionResult(grammar, tuple(stages))
