import json
from datetime import *

from . import models

timestamps = []


def event(file: str, level: str, msg: str, output: str) -> None:
    """Создание класса записываемого в отчёт сообщения"""
    e = models.createEvent(datetime.now(), file, level, msg)
    report(e, output)


def report(e: models.Event, output: str) -> None:
    """Запись сообщения в отчёт"""
    json_data = {
        "timestamp": str(e.timestamp.isoformat()[:-3] + "Z"),
        "level": e.level,
        "source": e.source,
        "message": e.message,
    }

    if len(timestamps) == 2:
        timestamps[1] = max(str(timestamps[1]), str(e.timestamp))
    else:
        timestamps.append(str(e.timestamp))

    if "Events" in e.message:
        json_data[
            "message"
        ] += f"First timestamp: {timestamps[0].replace(' ', 'T')[:-3]}Z Last timestamp: {timestamps[1].replace(' ', 'T')[:-3]}Z"

    try:
        with open(f"{output}", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
                if not isinstance(data, list):
                    data = [data]
            else:
                data = []
    except FileNotFoundError, json.JSONDecodeError:
        data = []

    data.append(json_data)

    with open(f"{output}", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
