class StreamStatsError(Exception):
    message = "Ошибка"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)

class WrongFormatError(StreamStatsError):
    default_message = "Error: wrong format"

class WrongEventError(StreamStatsError):
    default_message = "Error: wrong event"

class WrongTymestampError(StreamStatsError):
    default_message = "Error: wrong timestamp"

class WrongCLIConfError(StreamStatsError):
    default_message = "Error: wrong CLI configuration"