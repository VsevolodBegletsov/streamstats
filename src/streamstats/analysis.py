from . import parsers
from . import errors

def analyze(file, format, skip):
    if file.split(".")[-1] != format or file.split(".")[-1] not in ["csv", "jsonl"]:
        raise errors.WrongFormatError()
    if format == 'csv':
        res = parsers.parse_csv(file, skip)
    elif format == 'jsonl':
        res = parsers.parse_jsonl(file, skip)

    return res

def main(args):
    return analyze(args.INPUT, args.format, args.skip_invalid)
