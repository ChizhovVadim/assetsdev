from typing import NamedTuple
import datetime

# некоторые типы вместо datetime можно date
# В SplitInfo и DividendSchedule FixDate специально названы одинаково

class SplitInfo(NamedTuple):
    FixDate: datetime.datetime
    "Дата фиксации корпоративного действия"

    OldQuantity: int
    NewQuantity: int

# В идеале добавить инфу о дивидендах сюда
class SecurityInfo(NamedTuple):
    SecurityCode: str
    Title: str
    Number: str
    FinamCode: str
    MfdCode: str
    Splits: list[SplitInfo]

class ReceivedDividend(NamedTuple):
    Account: str
    Date: datetime.datetime
    Sum: float

class DividendSchedule(NamedTuple):
    SecurityCode: str
    FixDate: datetime.datetime
    "Дата фиксации корпоративного действия"
    
    Rate: float
    Received: list[ReceivedDividend] # Исторически полученные дивиденды храним здесь же, но лучше переделать
