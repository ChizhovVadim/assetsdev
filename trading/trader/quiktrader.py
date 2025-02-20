import datetime
import typing

import candles
from .import domaintypes
from .import forts
from .QuikPy import QuikPy

class QuikTrader:

	def __init__(self, port: int):
		# Игорь Чечет https://github.com/cia76/QuikPy
		# Есть также библиотеки для работы с finam, alor, T-invest: https://github.com/cia76?tab=repositories
		self._quik = QuikPy(requests_port=port, callbacks_port=port+1)
		self._transId = 1  #TODO init

	def close(self):
		self._quik.CloseConnectionAndThread()

	def setNewCandleCallback(self, handler: typing.Callable[[candles.Candle],None]):
		def f(data):
			handler(_parseQuikCandle(data["data"]))
		self._quik.OnNewCandle = f

	def isConnected(self)-> bool:
		resp = self._quik.IsConnected()
		return resp["data"] == 1

	def getLastCandles(self, security: domaintypes.SecurityInfo,
					candleInterval: candles.CandleInterval)-> list[candles.Candle]:
		#Если не указывать размер, то может прийти слишком много баров и unmarshal большой json
		MaxBars = 5_000
		new_bars = self._quik.GetCandlesFromDataSource(
			security.ClassCode, security.Code, _quikTimeframe(candleInterval), MaxBars)['data']
		new_bars = [_parseQuikCandle(c) for c in new_bars]
		# последний бар за сегодня может быть не завершен
		if new_bars and new_bars[-1].DateTime.date() == datetime.date.today():
			new_bars.pop()
		return new_bars
	
	def subscribeCandles(self, security: domaintypes.SecurityInfo,
					  candleInterval: candles.CandleInterval):
		self._quik.SubscribeToCandles(security.ClassCode, security.Code, _quikTimeframe(candleInterval))
	
	def incomingAmount(self, portfolio: domaintypes.PortfolioInfo)-> float:
		resp = self._quik.GetPortfolioInfoEx(portfolio.Firm, portfolio.Portfolio, 0)
		return float(resp["data"]["start_limit_open_pos"])
	
	def getPosition(self, portfolio: domaintypes.PortfolioInfo,
				 security: domaintypes.SecurityInfo)-> float:
		if security.ClassCode == forts.FUTURESCLASSCODE:
			resp = self._quik.GetFuturesHolding(portfolio.Firm, portfolio.Portfolio, security.Code, 0)
			return float(resp["data"]["totalnet"])

		raise NotImplementedError()
	
	def registerOrder(self, order: domaintypes.Order):
		pass
"""
		transaction = {  # Все значения должны передаваться в виде строк
			'ACTION': 'NEW_ORDER',
			'SECCODE': order.Security.Code,
			'CLASSCODE': order.Security.ClassCode,
			'ACCOUNT': order.Portfolio.Portfolio,
			'PRICE': forts.formatPrice(order.Price, order.Security.PricePrecision, order.Security.PriceStep),
			'TRANS_ID': str(self._transId),
			'CLIENT_CODE': str(self._transId),
		}
		self._transId += 1
		if order.Volume>0:
			transaction['OPERATION'] = "B"
			transaction['QUANTITY'] = str(order.Volume)
		else:
			transaction['OPERATION'] = "S"
			transaction['QUANTITY'] = str(-order.Volume)

		self._quik.SendTransaction(transaction)
"""

def _quikTimeframe(candleInterval: candles.CandleInterval):
	if candleInterval == candles.CandleInterval.MINUTES5:
		return 5
	raise ValueError("timeframe not supported", candleInterval)

def _parseQuikDateTime(dt)->datetime.datetime:
      return datetime.datetime(
            int(dt["year"]),
            int(dt["month"]),
            int(dt["day"]),
            int(dt["hour"]),
            int(dt["min"]),
            int(dt["sec"]))

def _parseQuikCandle(row) -> candles.Candle:
	return candles.Candle(
        SecurityCode=row["sec"],
		DateTime=_parseQuikDateTime(row["datetime"]),
		O=float(row["open"]),
		H=float(row["high"]),
		L=float(row["low"]),
		C=float(row["close"]),
		V=float(row["volume"]))
