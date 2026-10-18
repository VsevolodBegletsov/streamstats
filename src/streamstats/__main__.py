import sys
from argparse import *

from . import analysis, errors


def build_parser() -> ArgumentParser:
    """Создать парсер"""
    parser = ArgumentParser(
        prog = "streamstats",
        description = "Vsevolod Begletsov's Streamstats",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("INPUT")
    analyze_parser.add_argument("--format", dest="format", required=True)
    analyze_parser.add_argument("--output", dest="output_file", default="REPORT.json", required=True)
    analyze_parser.add_argument("--skip-invalid", action="store_true", required=False, default=False)

    analyze_parser.set_defaults(func=analysis.main)

    return parser

def main(argv: None) -> int:
    """Старт программы"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        analysis.main(args)
    except errors.StreamStatsError as e:
        print(e, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main(argv=None))