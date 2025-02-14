from typing import NamedTuple
import datetime

class MyTrade(NamedTuple):
    SecurityCode: str    
    DateTime: datetime.datetime
    ExecutionDate: datetime.datetime
    Price: float
    Volume: int
    ExchangeComission: float
    BrokerComission: float
    Account: str
