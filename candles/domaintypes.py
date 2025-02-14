from typing import NamedTuple
import datetime
import enum

class Candle(NamedTuple):
    SecurityCode: str
    DateTime: datetime.datetime
    O: float
    H: float
    L: float
    C: float
    V: float

class CandleInterval(enum.StrEnum):
    MINUTES5 = "minutes5"
    HOURLY = "hourly"
    DAILY = "daily"
