"""CLI de la primera etapa. El reconocimiento de frases corresponde a Miguel."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from cfg import convert_to_cnf, read_grammar


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simplificar una CFG y convertirla a Chomsky.")
    parser.add_argument("grammar", type=Path, help="Archivo de gramática")
    parser.add_argument("--start", help="Símbolo inicial (por defecto, cabecera o primera regla)")
    parser.add_argument("--output", type=Path, help="Guardar la CNF; por defecto, imprimirla")
    parser.add_argument("--trace-dir", type=Path, help="Guardar las etapas de transformación")
    args = parser.parse_args(argv)
    try:
        result = convert_to_cnf(read_grammar(args.grammar, start=args.start))
        if args.output:
            if args.output.resolve() == args.grammar.resolve():
                raise ValueError("La salida debe ser distinta del archivo de entrada.")
        if args.trace_dir:
            source = args.grammar.resolve()
            targets = [(args.trace_dir / f"{name}.txt").resolve() for name, _ in result.stages]
            if source in targets or (args.output and args.output.resolve() in targets):
                raise ValueError("Los archivos de etapas no deben coincidir con entrada o salida.")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result.grammar.to_text(), encoding="utf-8")
        else:
            print(result.grammar.to_text(), end="")
        if args.trace_dir:
            args.trace_dir.mkdir(parents=True, exist_ok=True)
            for name, grammar in result.stages:
                (args.trace_dir / f"{name}.txt").write_text(grammar.to_text(), encoding="utf-8")
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
