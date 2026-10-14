import csv
import json
import re

from . import report
from . import errors as error

err_messages = ["Too much parameters", "Too few parameters", "Wrong timestamp format"]
cr_messages = ["File not found", "Empty file"]
warn_messages = ["Empty element", "Wrong email format"]

msgs = {}

date_pattern =  r'\d+-\d+-\d+((T| )?\d+:\d+:\d+(?:\.\d+)?(?:Z|[+-]\d+:\d+)?)?'
correct_date_pattern =  r'\d{4}-\d{2}-\d{2}((T| )?\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?'

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

def timestamp_validation(timestamp):
    if timestamp.count('-') == 2:
        if (re.match(correct_date_pattern, timestamp)) and (1900 <= int(timestamp[:4]) <= 2100) and (1 <= int(timestamp[5:7]) <= 12) and (1 <= int(timestamp[8:10]) <= 31):
            return True
    else:
        if (re.match(correct_date_pattern, timestamp)) and (1900 <= int(timestamp[:4]) <= 2100) and (1<=int(timestamp[5:7])<=12) and (1 <= int(timestamp[8:10]) <= 31) and (0<=int(timestamp[11:13])<=23) and (0<=int(timestamp[14:16])<=59) and (0<=int(timestamp[17:19])<=59) and (0<=int(timestamp[-4:-1])<=999):
            return True
    return False

def is_timestamp(timestamp):
    match = re.match(date_pattern, timestamp)
    if match:
        return True
    else:
        return False

def print_top(msgs):
    c = 1
    line = ""
    msgs = dict(sorted(msgs.items(), key=lambda x: x[1], reverse=True))
    for i in msgs:
        if i in err_messages + cr_messages:
            line += f"{c}. {i}, {msgs[i]}; "
            c += 1
            if c == 5:
                break
    return line

def print_report(skip, f, counter, errors, warnings, critical, output):
    if skip and print_top(msgs):
        report.event(f.name, "INFO", f"Analyzing ended. "
                            f"Lines analyzed: {counter}, {errors + critical} skipped; "
                            f"Events: {errors + critical + warnings} ( "
                            f"WARNINGS: {warnings + errors}; "
                            f"ERRORS: {0}; "
                            f"CRITICAL ERRORS: {critical} ) "
                            f"Top-5 errors: {print_top(msgs)}", output)
    elif errors + critical == 0:
        report.event(f.name, "INFO", f"Analyzing ended. "
                            f"Lines analyzed: {counter}; "
                            f"Events: {errors + critical + warnings} ( "
                            f"WARNINGS: {warnings}; "
                            f"ERRORS: {errors}; "
                            f"CRITICAL ERRORS: {critical} )", output)

def parse_csv(file, skip, output):

    def analyze_line(counter, check, header, output):

        def validate(f, header, row, counter, skip, output):
            flag = 0
            c = 0
            source = f"{f.name}, Line: {counter + 1}"
            for i in row:
                c+=1

                if len(str(i)) == 0:
                    report.event(source, "WARNING", f"{warn_messages[0]} \"{i}\"", output)
                    add_to_dict(msgs, warn_messages[0])
                    flag = 1

                if is_timestamp(str(i)):
                    if timestamp_validation(str(i))==False:
                        add_to_dict(msgs, err_messages[2])
                        if skip:
                            report.event(source, "WARNING", err_messages[2], output)
                            report.event(source, "DEBUG", "Skipping line...", output)
                        else:
                            report.event(source, "ERROR", err_messages[2], output)
                            raise error.WrongTimestampError()
                        flag = 1

            if c < len(header):
                if skip:
                    report.event(source, "WARNING", err_messages[1], output)
                    report.event(source, "DEBUG", "Skipping line...", output)
                else: report.event(source, "ERROR", err_messages[1], output)
                add_to_dict(msgs, err_messages[1])
                flag = 1

            if c > len(header):
                if skip:
                    report.event(source, "WARNING", err_messages[0], output)
                    report.event(source, "DEBUG", "Skipping line...", output)
                else: report.event(source, "ERROR", err_messages[0], output)
                add_to_dict(msgs, err_messages[0])
                flag = 1

            if flag:
                return counter - 1, flag
            return counter, flag

        for row in reader:

            if check == 0:
                header = row
                check = 1
                continue

            counter += 1

            gl_counter, flag = validate(f, header, row, counter, skip, output)

            errors = count_msg(msgs, err_messages)
            warnings = count_msg(msgs, warn_messages)
            critical = count_msg(msgs, cr_messages)

            if (skip == False and (errors + critical) > 0):
                return 2

            if flag == 0:
                report.event(f"{f.name}, Line: {counter}", "DEBUG", "Line analyzed", output)

        return errors, warnings, critical, counter, gl_counter

    counter = 0
    check = 0
    header = []

    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        errors, warnings, critical, counter, gl_counter = analyze_line(counter, check, header, output)
        print_report(skip, f, gl_counter-(errors+warnings+critical), errors, warnings, critical, output)

def parse_jsonl(file, skip, output):

    def analyze_line(counter, check, header, output):

        def validate(f, header, row, counter, skip, output):
            flag = 0
            c = 0
            source = f"{f.name}, Line: {counter}"

            for i in row:
                c += 1
                if i not in header:
                    if skip:
                        report.event(source, "WARNING", err_messages[0], output)
                        report.event(source, "DEBUG", "Skipping line...", output)
                    else: report.event(source, "ERROR", err_messages[0], output)
                    add_to_dict(msgs, err_messages[0])
                    flag = 1

                if len(str(row[i])) == 0:
                    report.event(source, "WARNING", warn_messages[0], output)
                    add_to_dict(msgs, warn_messages[0])
                    flag = 1
                    #report.event(source, "DEBUG", "Skipping line...")

                if is_timestamp(str(row[i])):
                    if timestamp_validation(str(row[i]))==False:
                        add_to_dict(msgs, err_messages[2])
                        if skip:
                            report.event(source, "WARNING", err_messages[2], output)
                            report.event(source, "DEBUG", "Skipping line...", output)
                        else:
                            report.event(source, "ERROR", f"{error.WrongTimestampError.default_message}", output)
                            raise error.WrongTimestampError
                        flag = 1

            if c < len(header):
                if skip:
                    report.event(source, "WARNING", err_messages[1], output)
                    report.event(source, "DEBUG", "Skipping line...", output)
                else: report.event(source, "ERROR", err_messages[1], output)
                add_to_dict(msgs, err_messages[1])
                flag = 1

            if flag:
                return counter - 1, flag
            return counter, flag

        for row in f:

            counter += 1

            row = row.strip()
            row = json.loads(row)
            if check == 0:
                for i in row: header.append(i)
                check = 1

            gl_counter, flag = validate(f, header, row, counter, skip, output)

            errors = count_msg(msgs, err_messages)
            warnings = count_msg(msgs, warn_messages)
            critical = count_msg(msgs, cr_messages)

            if (skip == False and (errors + critical) > 0):
                return 2

            if flag==0:
                report.event(f"{f.name}, Line: {counter}", "DEBUG", "Line analyzed", output)

        return errors, warnings, critical, counter, gl_counter

    counter = 0
    check = 0
    header = []

    with open(file, 'r', encoding='utf-8') as f:
        try:
            errors, warnings, critical, counter, gl_counter = analyze_line(counter, check, header, output)
            print_report(skip, f, gl_counter-(errors+warnings+critical)+1, errors, warnings, critical, output)
        except error.WrongTimestampError:
            raise
        except:
            return 2
