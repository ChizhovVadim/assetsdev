import datetime

import candles
from .import domaintypes
from .import forts
from .QuikPy import QuikPy

class QuikTrader:

	def __init__(self, port: int):
		# Игорь Чечет https://github.com/cia76/QuikPy
		# Есть также библиотеки для работы с finam, alor, T-invest: https://github.com/cia76?tab=repositories
		self._quik = QuikPy(requests_port=port, callbacks_port=port+1)

	def Close(self):
		self._quik.CloseConnectionAndThread()

	def IsConnected(self)-> bool:
		resp = self._quik.IsConnected()
		return resp["data"] == 1

	def GetLastCandles(self, security: domaintypes.SecurityInfo,
					candleInterval: candles.CandleInterval)-> list[candles.Candle]:
		new_bars = self._quik.GetCandlesFromDataSource(
			security.ClassCode, security.Code, _quikTimeframe(candleInterval), 0)['data']
		new_bars = [_parseQuikCandle(c) for c in new_bars]
		# последний бар за сегодня может быть не завершен
		if new_bars and new_bars[-1].DateTime.date() == datetime.date.today():
			new_bars.pop()
		return new_bars
	
	def SubscribeCandles(self, security: domaintypes.SecurityInfo,
					  candleInterval: candles.CandleInterval):
		self._quik.SubscribeToCandles(security.ClassCode, security.Code, _quikTimeframe(candleInterval))
	
	def IncomingAmount(self, portfolio: domaintypes.PortfolioInfo)-> float:
		resp = self._quik.GetPortfolioInfoEx(portfolio.Firm, portfolio.Portfolio, 0)
		return float(resp["data"]["start_limit_open_pos"])
	
	def GetPosition(self, portfolio: domaintypes.PortfolioInfo,
				 security: domaintypes.SecurityInfo)-> int:
		#if security.ClassCode == forts.FUTURESCLASSCODE:

		raise NotImplementedError()
	
	def RegisterOrder(self, order: domaintypes.Order):
		raise NotImplementedError()


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
