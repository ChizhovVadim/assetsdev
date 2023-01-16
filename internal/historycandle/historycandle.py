from dataclasses import dataclass
import datetime

@dataclass(frozen=True)
class HistoryCandle:
    DateTime: datetime.datetime
    O: float
    H: float
    L: float
    C: float
    V: float
