from . import parsers

import csv

def analyze(file, format, skip):
    if format == 'csv':
        parsers.parse_csv(file, skip)
    else:
        parsers.parse_jsonl(file, skip)

def main(args):
    return analyze(args.INPUT, args.format, args.skip_invalid)
