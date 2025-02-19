from typing import NamedTuple

class Client(NamedTuple):
	Key: str
	Firm: str
	Portfolio: str
	Amount: float|None
	MaxAmount: float|None
	Weight: float|None
	Port: int

class StrategyConfig(NamedTuple):
	Name: str
	SecurityCode: str
	Lever: float
	MaxLever: float
	Weight: float
	StdVolatility: float
	Direction: int
	Position: float

class TraderSettings(NamedTuple):
	Clients: list[Client]
	StrategyConfigs: list[StrategyConfig]

class SecurityInfo(NamedTuple):
	Name: str
	"Название инструмента"
	Code: str
	"Код инструмента"
	ClassCode: str
	"Код класса"
	PricePrecision: int
	"точность (кол-во знаков после запятой). Если шаг цены может быть не круглым (0.05), то этого будет недостаточно."
	PriceStep: float
	"шаг цены"
	PriceStepCost: float
	"Стоимость шага цены"
	Lever: float
	"Плечо. Для фьючерсов = PriceStepCost/PriceStep."

class PortfolioInfo(NamedTuple):
	Firm: str
	Portfolio: str

class Order(NamedTuple):
	Portfolio: PortfolioInfo
	Security: SecurityInfo
	Volume: int
	Price: float
