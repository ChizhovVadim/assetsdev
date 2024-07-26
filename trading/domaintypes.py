import datetime
from typing import NamedTuple, Any

class Advice(NamedTuple):
	SecurityCode: str
	DateTime: datetime.datetime
	Price: float
	Position: float
	Details: Any

class DateSum(NamedTuple):
	DateTime: datetime.datetime
	Sum: float

class SecurityCode(NamedTuple):
	Code: str
	FinamCode: str
	MfdCode: str

class StrategyConfig(NamedTuple):
	Name: str
	SecurityCode: str
	Lever: float
	MaxLever: float
	Weight: float
	StdVolatility: float
	Direction: int
	Position: float

class StrategySettings(NamedTuple):
	SecurityCodes: list[SecurityCode]
	StrategyConfigs: list[StrategyConfig]#Можно нетипизированные?

class Client(NamedTuple):
	Key: str
	Firm: str
	Portfolio: str
	Amount: float
	MaxAmount: float
	Weight: float
	Port: int

class TraderSettings(NamedTuple):
	Clients: list[Client]
