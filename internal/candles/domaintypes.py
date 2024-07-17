from typing import NamedTuple
import datetime
import enum

class Candle(NamedTuple):
    #SecurityCode: str
    DateTime: datetime.datetime
    O: float
    H: float
    L: float
    C: float
    V: float

class Timeframe(enum.IntEnum):
    MINUTES5 = 0
    HOURLY = 1
    DAILY = 2
