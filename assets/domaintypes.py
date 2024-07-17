from typing import NamedTuple
import datetime

class SecurityInfo(NamedTuple):
    SecurityCode: str
    Title: str
    Number: str
    FinamCode: str
    MfdCode: str

class MyTrade(NamedTuple):
    SecurityCode: str    
    DateTime: datetime.datetime
    ExecutionDate: datetime.datetime
    Price: float
    Volume: int
    ExchangeComission: float
    BrokerComission: float
    Account: str

class ReceivedDividend(NamedTuple):
    Account: str
    Date: datetime.date
    Sum: float

class DividendSchedule(NamedTuple):
    SecurityCode: str
    RecordDate: datetime.datetime
    Rate: float
    Received: list[ReceivedDividend]
