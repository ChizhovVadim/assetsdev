import candles
from .import domaintypes

class MockTrader:
	def __init__(self):
		self._positions = dict()

	def Close(self):
		pass

	def IsConnected(self)-> bool:
		return True
	
	def GetLastCandles(self, security: domaintypes.SecurityInfo,
					candleInterval: candles.CandleInterval)-> list[candles.Candle]:
		return []
	
	def SubscribeCandles(self, security: domaintypes.SecurityInfo,
					  candleInterval: candles.CandleInterval):
		pass
	
	def IncomingAmount(self, portfolio: domaintypes.PortfolioInfo)-> float:
		return 1_000_000
	
	def GetPosition(self, portfolio: domaintypes.PortfolioInfo,
				 security: domaintypes.SecurityInfo)-> int:
		return self._positions.get(security.Code, 0)
	
	def RegisterOrder(self, order: domaintypes.Order):
		self._positions[order.Security.Code] = self._positions.get(order.Security.Code, 0) 
		+ order.Volume
