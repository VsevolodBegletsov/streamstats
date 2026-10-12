from . import models

def error(file, msg):
    e = models.createEvent(file, "ERROR", msg)
    report(e)

def warning(file, msg):
    e = models.createEvent(file, "WARNING", msg)
    report(e)

def info(file, msg):
    e = models.createEvent(file, "INFO", msg)
    report(e)

def info_top(file, msg):
    e = models.createEvent(file, "INFO", msg)
    report(e)

def debug(file, msg):
    e = models.createEvent(file, "DEBUG", msg)
    report(e)

def critical(file, msg):
    e = models.createEvent(file, "CRITICAL", msg)
    report(e)

def report(e):
    print(" timestamp:", e.timestamp, '\n',
          "level:", e.level, '\n',
          "source:", e.source, '\n',
          "message:", e.message, '\n')