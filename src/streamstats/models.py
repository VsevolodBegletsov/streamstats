from datetime import *

time = datetime.now()

class Event:
    timestamp: str
    level: str
    source: str
    message: str

def createEvent(file, level, msg):
    e = Event()
    e.timestamp = str(time)
    e.level = level
    e.source = file
    e.message = msg
    return e