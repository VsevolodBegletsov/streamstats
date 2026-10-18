class Event:
    """Класс сообщения"""
    timestamp: str
    level: str
    source: str
    message: str

def createEvent(timestamp: str, file: str, level: str, msg: str) -> Event:
    """Создание объекта сообщения"""
    e = Event()
    e.timestamp = timestamp
    e.level = level
    e.source = file
    e.message = msg
    return e