import csv
import json
import re
from typing import TextIO

from . import errors as error
from . import report

err_messages = ["Too much parameters", "Too few parameters", "Wrong timestamp format", "Empty line"]
cr_messages = ["Empty file"]
warn_messages = ["Empty element", "Wrong email format"]

msgs = {}

date_pattern =  r'\d+-\d+-\d+((T| )?\d+:\d+:\d+(?:\.\d+)?(?:Z|[+-]\d+:\d+)?)?'
correct_date_pattern =  r'\d{4}-\d{2}-\d{2}((T| )?\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?'

def add_to_dict(messages: dict, key: str) -> None:
    """Добавить сообщение об ошибке в словарь"""
    if key in messages:
        messages[key] += 1
    else:
        messages[key] = 1

def count_msg(messages: dict, arr: list) -> int:
    """Посчитать кол-во ошибок"""
    temp = 0
    for i, value in messages.items():
        if i in arr:
            temp += value
    return temp

def timestamp_validation(timestamp: str) -> bool:
    """Проверка формата временной отметки"""
    if timestamp.count('-') == 2:
        if (re.match(correct_date_pattern, timestamp)) and (1900 <= int(timestamp[:4]) <= 2100) and (1 <= int(timestamp[5:7]) <= 12) and (1 <= int(timestamp[8:10]) <= 31):
            return True
    else:
        if (re.match(correct_date_pattern, timestamp)) and (1900 <= int(timestamp[:4]) <= 2100) and (1<=int(timestamp[5:7])<=12) and (1 <= int(timestamp[8:10]) <= 31) and (0<=int(timestamp[11:13])<=23) and (0<=int(timestamp[14:16])<=59) and (0<=int(timestamp[17:19])<=59) and (0<=int(timestamp[-4:-1])<=999):
            return True
    return False

def is_timestamp(timestamp: str) -> bool:
    """Определяет, является ли элемент временной отметкой"""
    match = re.match(date_pattern, timestamp)
    return bool(match)

def print_top(msgs: dict) -> str:
    """Формирует Топ-5 самых частых ошибок"""
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

def print_report(skip: bool, f: TextIO, counter: int, errors: int, warnings: int, critical: int, debug: int, output: str) -> None:
    """Создание финального сообщения о завершении анализа файла"""
    if skip and print_top(msgs):
        report.event(f.name, "INFO", f"Analyzing ended. "
                            f"Lines analyzed: {debug-warnings}, {errors+critical} skipped; "
                            f"Events: {warnings + debug + 2} ( "
                            f"DEBUGS: {debug}; "
                            f"INFOS: 2; "
                            f"WARNINGS: {warnings}; "
                            f"ERRORS: 0; "
                            f"CRITICAL ERRORS: {critical} ) "
                            f"Top-5 errors: {print_top(msgs)}", output)
    elif errors + critical == 0:
        report.event(f.name, "INFO", f"Analyzing ended. "
                            f"Lines analyzed: {counter}; "
                            f"Events: {warnings + debug + 2} ( "
                            f"DEBUGS: {debug}; "
                            f"INFOS: 2; "
                            f"WARNINGS: {warnings}; "
                            f"ERRORS: 0; "
                            f"CRITICAL ERRORS: 0 )", output)
    else:
        report.event(f.name, "INFO", f"Analyzing ended prematurely. "
                                     f"Lines analyzed: {counter}; "
                                     f"Events: {errors + critical + warnings + debug + 2} ( "
                                     f"DEBUGS: {debug}; "
                                     f"INFOS: 2; "
                                     f"WARNINGS: {warnings}; "
                                     f"ERRORS: {errors}; "
                                     f"CRITICAL ERRORS: {critical} ) ", output)

def parse_csv(file: str, skip: bool, output: str) -> None:
    """Парсинг csv-таблицы"""

    def analyze_line(counter: int, check: bool, header: list, output: str) -> tuple[int, int, int, int, int, int]:
        """Анализ переданного события"""

        def validate(f: TextIO, header: list, row: list, counter: int, skip: bool, output: str, debug: int, warnings: int) -> tuple[int, bool, int, int]:
            """Валидация события, поиск ошибок"""
            flag = False
            c = 0
            source = f"{f.name}, Line: {counter}"

            if len(row) == 0:
                add_to_dict(msgs, err_messages[3])
                if skip:
                    report.event(source, "WARNING", err_messages[3], output)
                    warnings+=1
                    report.event(source, "DEBUG", "Skipping line...", output)
                    debug += 1
                    flag = True
                    return counter - 1, flag, debug, warnings
                else:
                    report.event(source, "ERROR", err_messages[3], output)
                    print_report(skip, f, counter, errors+1, warnings, critical, debug, output)
                    raise error.WrongEventError()

            for i in row:
                c+=1

                if len(str(i)) == 0:
                    report.event(source, "WARNING", f"{warn_messages[0]} \"{i}\"", output)
                    warnings+=1
                    flag = True

                if is_timestamp(str(i)) and timestamp_validation(str(i))==False:
                    add_to_dict(msgs, err_messages[2])
                    if skip:
                        report.event(source, "WARNING", err_messages[2], output)
                        warnings+=1
                    else:
                        report.event(source, "ERROR", err_messages[2], output)
                        print_report(skip, f, counter, errors+1, warnings, critical, debug, output)
                        raise error.WrongTimestampError()
                    flag = True

            if c < len(header):
                add_to_dict(msgs, err_messages[1])
                if skip:
                    report.event(source, "WARNING", err_messages[1], output)
                    warnings+=1
                else:
                    report.event(source, "ERROR", err_messages[1], output)
                    print_report(skip, f, counter, errors+1, warnings, critical, debug, output)
                    raise error.WrongEventError()
                flag = True

            if c > len(header):
                add_to_dict(msgs, err_messages[0])
                if skip:
                    report.event(source, "WARNING", err_messages[0], output)
                    warnings+=1
                else:
                    report.event(source, "ERROR", err_messages[0], output)
                    print_report(skip, f, counter, errors+1, warnings, critical, debug, output)
                    raise error.WrongEventError()
                flag = True

            if flag:
                if skip:
                    report.event(source, "DEBUG", "Skipping line...", output)
                    debug += 1
                return counter - 1, flag, debug, warnings
            return counter, flag, debug, warnings

        debug = 0
        warnings = 0
        errors = 0
        critical = 0

        for row in reader:

            if check == 0:
                header = row
                check = 1
                continue

            counter += 1

            gl_counter, flag, debug, warnings = validate(f, header, row, counter, skip, output, debug, warnings)

            errors = count_msg(msgs, err_messages)
            critical = count_msg(msgs, cr_messages)

            if (skip == False and (errors + critical) > 0):
                raise error.StreamStatsError

            if flag == 0:
                report.event(f"{f.name}, Line: {counter}", "DEBUG", f"Line {row} analyzed", output)
                debug+=1

        if check == 0:
            report.event(f.name, "CRITICAL", cr_messages[0], output)
            raise error.StreamStatsError
        return errors, warnings, critical, debug, counter, gl_counter

    counter = 0
    check = 0
    header = []

    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        errors, warnings, critical, debug, counter, gl_counter = analyze_line(counter, check, header, output)
        print_report(skip, f, gl_counter-(errors+critical), errors, warnings, critical, debug, output)

def parse_jsonl(file: str, skip: bool, output: str) -> None:
    """Парсинг jsonl-таблицы"""

    def analyze_line(counter: int, check: bool, header: list, output: str) -> tuple[int, int, int, int, int, int]:
        """Анализ переданного события"""

        def validate(f: TextIO, header: list, row: list, counter: int, skip: bool, output: str, debug: int, warnings: int):
            """Валидация события, поиск ошибок"""
            flag = False
            c = 0
            source = f"{f.name}, Line: {counter}"

            for i in row:
                c += 1
                if i not in header:
                    add_to_dict(msgs, err_messages[0])
                    if skip:
                        report.event(source, "WARNING", err_messages[0], output)
                        warnings += 1
                    else:
                        report.event(source, "ERROR", err_messages[0], output)
                        print_report(skip, f, counter, errors + 1, warnings, critical, debug, output)
                        raise error.WrongEventError()
                    flag = 1

                if len(str(row[i])) == 0:
                    report.event(source, "WARNING", warn_messages[0], output)
                    add_to_dict(msgs, warn_messages[0])
                    warnings += 1
                    flag = 1
                    #report.event(source, "DEBUG", "Skipping line...")

                if is_timestamp(str(row[i])) and timestamp_validation(str(row[i]))==False:
                    add_to_dict(msgs, err_messages[2])
                    if skip:
                        report.event(source, "WARNING", err_messages[2], output)
                        warnings += 1
                    else:
                        report.event(source, "ERROR", f"{error.WrongTimestampError.default_message}", output)
                        print_report(skip, f, counter, errors + 1, warnings, critical, debug, output)
                        raise error.WrongTimestampError
                    flag = 1

            if c < len(header):
                add_to_dict(msgs, err_messages[1])
                if skip:
                    report.event(source, "WARNING", err_messages[1], output)
                    warnings += 1
                else:
                    report.event(source, "ERROR", err_messages[1], output)
                    print_report(skip, f, counter, errors + 1, warnings, critical, debug, output)
                    raise error.WrongEventError()
                flag = 1

            if flag:
                if skip:
                    report.event(source, "DEBUG", "Skipping line...", output)
                    debug += 1
                return counter - 1, flag, debug, warnings
            return counter, flag, debug, warnings

        debug = 0
        warnings = 0
        errors = 0
        critical = 0

        header_copy = header.copy()

        for row in f:

            counter += 1

            row = row.strip()
            row = json.loads(row)
            if check == 0:
                for i in row: header_copy.append(i)
                if header_copy == []:
                    report.event(f, "CRITICAL", cr_messages[0], output)
                    raise error.StreamStatsError
                check = 1

            gl_counter, flag, debug, warnings = validate(f, header_copy, row, counter, skip, output, debug, warnings)

            errors = count_msg(msgs, err_messages)
            critical = count_msg(msgs, cr_messages)

            if (skip == False and (errors + critical) > 0):
                raise error.StreamStatsError

            if flag==0:
                report.event(f"{f.name}, Line: {counter}", "DEBUG", f"Line {row} analyzed", output)
                debug+=1

        if check == 0:
            report.event(f.name, "CRITICAL", cr_messages[0], output)
            raise error.StreamStatsError

        return errors, warnings, critical, debug, counter, gl_counter

    counter = 0
    check = 0
    header = []

    with open(file, 'r', encoding='utf-8') as f:
        errors, warnings, critical, debug, counter, gl_counter = analyze_line(counter, check, header, output)
        print_report(skip, f, gl_counter-(errors+critical), errors, warnings, critical, debug, output)
        return 0