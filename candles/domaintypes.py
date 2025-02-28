from typing import NamedTuple
import datetime
import enum

class Candle(NamedTuple):
    SecurityCode: str
    DateTime: datetime.datetime
    OpenPrice: float
    HighPrice: float
    LowPrice: float
    ClosePrice: float
    Volume: float

class CandleInterval(enum.StrEnum):
    MINUTES5 = "minutes5"
    HOURLY = "hourly"
    DAILY = "daily"
