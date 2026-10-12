"""Mediciones reproducibles del intervalo de reconocimiento, sin dependencias."""

import argparse
from pathlib import Path
import platform
from statistics import median

from cfg import convert_to_cnf, cyk, read_grammar

EXAMPLES = (
    "she eats a cake with a fork",
    "the cat drinks the beer",
    "he cooks",
    "she eats",
    "the cake drinks a knife",
    "she eats cake",
    "cat drinks the beer",
    "she dances",
    "",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=100, help="Repeticiones por frase (por defecto 100)")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat debe ser positivo")
    grammar = convert_to_cnf(read_grammar(Path(__file__).resolve().parent / "data/ingles.txt")).grammar
    print(f"Python {platform.python_version()}; {platform.system()} {platform.machine()}; {args.repeat} repeticiones")
    print("| Frase | Tokens | Aceptada | Mediana (ms) |")
    print("| --- | ---: | --- | ---: |")
    for phrase in EXAMPLES:
        tokens = phrase.split()
        cyk(grammar, tokens)  # Una ejecución de calentamiento, excluida de la mediana.
        results = [cyk(grammar, tokens) for _ in range(args.repeat)]
        duration = median(result.elapsed_seconds for result in results) * 1000
        print(f"| {phrase or '(vacía)'} | {len(tokens)} | {'SÍ' if results[0].accepted else 'NO'} | {duration:.6f} |")


if __name__ == "__main__":
    main()
