from . import models
from datetime import *
import json

def error(file, msg):
    e = models.createEvent(datetime.now(), file, "ERROR", msg)
    report(e)

def warning(file, msg):
    e = models.createEvent(datetime.now(), file, "WARNING", msg)
    report(e)

def info(file, msg):
    e = models.createEvent(datetime.now(), file, "INFO", msg)
    report(e)

def debug(file, msg):
    e = models.createEvent(datetime.now(), file, "DEBUG", msg)
    report(e)

def critical(file, msg):
    e = models.createEvent(datetime.now(), file, "CRITICAL", msg)
    report(e)

def report(e):
    json_data = {"timestamp":  str(e.timestamp),
                 "level": e.level,
                 "source": e.source,
                 "message": e.message }
    #print(json_data)
    with open('report.json', 'a+', encoding='utf-8') as outfile:
        #f_data = json.load(outfile)
        json.dump(json_data, outfile, ensure_ascii=False, indent=4)
        outfile.write(',\n')
    outfile.close()