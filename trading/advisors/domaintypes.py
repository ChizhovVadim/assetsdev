import datetime
from typing import NamedTuple, Any

class Advice(NamedTuple):
	SecurityCode: str
	DateTime: datetime.datetime
	Price: float
	Position: float
	Details: Any
