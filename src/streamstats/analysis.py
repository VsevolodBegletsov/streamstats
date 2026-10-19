from argparse import Namespace
from pathlib import Path

from . import errors, parsers, report


def analyze(file: str, format: str, skip: bool, output: str) -> None:
    """Первичная проверка файла и начало его анализа"""
    try:
        if not Path(file).is_file():
            raise errors.WrongCLIConfError()

        report.event(file, "INFO", "Starting analyzing...", output)

        if file.split(".")[-1] != format or file.split(".")[-1] not in ["csv", "jsonl"]:
            raise errors.WrongFormatError()

        if format == "csv":
            parsers.parse_csv(file, skip, output)
        elif format == "jsonl":
            parsers.parse_jsonl(file, skip, output)

    except errors.WrongCLIConfError:
        report.event(
            file, "CRITICAL", f"{errors.WrongCLIConfError.default_message}", output
        )
        raise
    except errors.WrongFormatError:
        report.event(
            file, "CRITICAL", f"{errors.WrongFormatError.default_message}", output
        )
        raise


def main(args: Namespace) -> None:
    """Запуск функции анализа файла"""
    return analyze(args.INPUT, args.format, args.skip_invalid, args.output_file)
