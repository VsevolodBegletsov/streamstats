from . import parsers
from . import errors
from . import report
from pathlib import Path

def analyze(file, format, skip, output):
    if not Path(file).is_file():
        report.event(file, "CRITICAL", f"{errors.WrongCLIConfError.default_message}", output)
        raise errors.WrongCLIConfError()
    report.event(file, "INFO", "Starting analyzing...", output)
    if file.split(".")[-1] != format or file.split(".")[-1] not in ["csv", "jsonl"]:
        report.event(file, "CRITICAL", f"{errors.WrongFormatError.default_message}", output)
        raise errors.WrongFormatError()
    if format == 'csv':
        res = parsers.parse_csv(file, skip, output)
    elif format == 'jsonl':
        res = parsers.parse_jsonl(file, skip, output)

    return res



def main(args):
    return analyze(args.INPUT, args.format, args.skip_invalid, args.output_file)
