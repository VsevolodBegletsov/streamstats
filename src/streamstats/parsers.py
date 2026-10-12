import csv
import json

from . import report

err_messages = ["Too much parameters", "Too few parameters"]
cr_messages = ["Critical error"]
warn_messages = ["Empty element", "Wrong email format"]

msgs = {}

def add_to_dict(dict, key):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def count_msg(dict, arr):
    temp = 0
    for i in dict:
        if i in arr:
            temp += dict[i]
    return temp

def print_top(msgs):
    c = 1
    line = ""
    msgs = dict(sorted(msgs.items(), key=lambda x: x[1], reverse=True))
    for i in msgs:
        if i in err_messages + cr_messages:
            line += f"{c}. {i}, {msgs[i]} \n\t\t\t"
            c += 1
            if c == 5:
                break
    return line

def print_report(skip, f, counter, errors, warnings, critical):
    if skip and print_top(msgs):
        report.info(f.name, f"Analyzing ended. "
                            f"Lines analyzed: {counter - 1}; "
                            f"Events: {errors + critical + warnings} ( "
                            f"WARNINGS: {warnings + errors}; "
                            f"ERRORS: {0}; "
                            f"CRITICAL ERRORS: {critical} )\n"
                            f"          Top-5 errors: {print_top(msgs)}")
    elif errors + critical == 0:
        report.info(f.name, f"Analyzing ended. "
                            f"Lines analyzed: {counter - 1}; "
                            f"Events: {errors + critical + warnings} ( "
                            f"WARNINGS: {warnings}; "
                            f"ERRORS: {errors}; "
                            f"CRITICAL ERRORS: {critical} )")
    else:
        report.info(f.name, f"Analyzing ended prematurely with error. Lines analyzed: {counter - 1} ")

def parse_csv(file, skip):

    def analyze_line(counter, check, header):

        def validate(f, header, row, counter):
            c = 0
            source = f"{f.name}, Line: {counter - 1}"
            for i in row:
                c+=1

                if len(str(i)) == 0:
                    report.warning(source, f"{warn_messages[0]} \"{i}\"")
                    add_to_dict(msgs, warn_messages[0])
                    continue

            if c < len(header):
                report.error(source, err_messages[1])
                add_to_dict(msgs, err_messages[1])
                return counter - 1

            if c > len(header):
                report.error(source, err_messages[0])
                add_to_dict(msgs, err_messages[0])
                return counter - 1

            return counter

        for row in reader:

            counter += 1

            if check == 0:
                header = row
                check = 1
                continue

            counter = validate(f, header, row, counter)

            errors = count_msg(msgs, err_messages)
            warnings = count_msg(msgs, warn_messages)
            critical = count_msg(msgs, cr_messages)

            if (skip == False and (errors + critical) > 0):
                break

        return errors, warnings, critical, counter

    counter = 1
    check = 0
    header = []

    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        errors, warnings, critical, counter = analyze_line(counter, check, header)
        print_report(skip, f, counter, errors, warnings, critical)

def parse_jsonl(file, skip):

    def analyze_line(counter, check, header):

        def validate(f, header, row, counter):
            c = 0
            source = f"{f.name}, Line: {counter - 1}"

            for i in row:
                c += 1
                if i not in header:
                    report.error(source, err_messages[0])
                    add_to_dict(msgs, err_messages[0])
                    return counter - 1

                if len(str(row[i])) == 0:
                    report.warning(source, f"{warn_messages[0]} \"{i}\"")
                    add_to_dict(msgs, warn_messages[0])
                    return counter - 1

                if i == 'email' and (row[i].count('@') != 1 or row[i].count('.') != 1):
                    report.warning(source, warn_messages[1])
                    add_to_dict(msgs, warn_messages[1])

            if c < len(header):
                report.error(source, err_messages[1])
                add_to_dict(msgs, err_messages[1])
                return counter - 1

            return counter

        for row in f:

            counter += 1

            row = row.strip()
            row = json.loads(row)
            if check == 0:
                for i in row: header.append(i)
                check = 1

            counter = validate(f, header, row, counter)

            errors = count_msg(msgs, err_messages)
            warnings = count_msg(msgs, warn_messages)
            critical = count_msg(msgs, cr_messages)

            if (skip == False and (errors + critical) > 0):
                break

        return errors, warnings, critical, counter

    counter = 1
    check = 0
    header = []

    try:
        with open(file, 'r', encoding='utf-8') as f:
            errors, warnings, critical, counter = analyze_line(counter, check, header)
            print_report(skip, f, counter, errors, warnings, critical)
    except:
        raise ValueError()