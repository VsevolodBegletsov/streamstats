from . import models
from datetime import *
import json

timestamps = []

def event(file, level, msg, output):
    e = models.createEvent(datetime.now(), file, level, msg)
    report(e, output)

def report(e, output):
    json_data = { "timestamp":  str(e.timestamp.isoformat()[:-3]+'Z'),
                 "level": e.level,
                 "source": e.source,
                 "message": e.message }

    if len(timestamps) == 2:
        timestamps[1] = max(str(timestamps[1]), str(e.timestamp))
    else:
        timestamps.append(str(e.timestamp))

    if "Events" in e.message:
        json_data["message"] += f"First timestamp: {timestamps[0]} Last timestamp: {timestamps[1]}"

    try:
        with open(f'{output}', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
                if not isinstance(data, list):
                    data = [data]
            else:
                data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(json_data)

    with open(f'{output}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
