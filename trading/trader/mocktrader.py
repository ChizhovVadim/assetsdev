import typing

import candles
from .import domaintypes

class MockTrader:
	def __init__(self):
		self._positions = dict()

	def close(self):
		pass

	def setNewCandleCallback(self, handler: typing.Callable[[candles.Candle],None]):
		pass

	def isConnected(self)-> bool:
		return True
	
	def getLastCandles(self, security: domaintypes.SecurityInfo,
					candleInterval: candles.CandleInterval)-> list[candles.Candle]:
		return []
	
	def subscribeCandles(self, security: domaintypes.SecurityInfo,
					  candleInterval: candles.CandleInterval):
		pass
	
	def incomingAmount(self, portfolio: domaintypes.PortfolioInfo)-> float:
		return 1_000_000
	
	def getPosition(self, portfolio: domaintypes.PortfolioInfo,
				 security: domaintypes.SecurityInfo)-> int:
		return self._positions.get(security.Code, 0)
	
	def registerOrder(self, order: domaintypes.Order):
		self._positions[order.Security.Code] = self._positions.get(order.Security.Code, 0) 
		+ order.Volume
