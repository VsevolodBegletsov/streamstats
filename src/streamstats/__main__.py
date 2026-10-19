import sys
from argparse import *

from . import analysis, errors


def build_parser() -> ArgumentParser:
    """Создать парсер"""
    parser = ArgumentParser(
        prog="streamstats",
        description="Vsevolod Begletsov's Streamstats",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Format: INPUT --format FORMAT --output OUTPUT (--skip-invalid)")
    analyze_parser.add_argument("INPUT", help="Enter file address")
    analyze_parser.add_argument("--format", dest="format", help="Enter file fotmat", required=True)
    analyze_parser.add_argument(
        "--output", dest="output_file", help="Enter output file name", default="REPORT.json", required=True
    )
    analyze_parser.add_argument(
        "--skip-invalid", action="store_true", help="Enter --skip-invalid if you want to skip errors", required=False, default=False
    )

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
