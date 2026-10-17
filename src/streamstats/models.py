from datetime import *


class Event:
    timestamp: str
    level: str
    source: str
    message: str

def createEvent(timestamp, file, level, msg):
    e = Event()
    e.timestamp = timestamp
    e.level = level
    e.source = file
    e.message = msg
    return e