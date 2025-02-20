import logging
import datetime
import queue

import candles
from trading.advisors import Advice
from .import domaintypes

class Advisor:
      def __init__(self,
            advisor,
            security: domaintypes.SecurityInfo,
            start: datetime.datetime,
            queue: queue.Queue,
            ):
            self._advisor = advisor
            self._security = security
            self._start = start
            self._queue = queue

      def initCandles(self, candles):
            initAdvice = None
            for candle in candles:
                  advice = self._advisor(candle)
                  if advice is not None:
                        initAdvice = advice
            logging.info(f"Init advice {initAdvice}")

      def onNewCandle(self, candle: candles.Candle):
            if self._security.Code != candle.SecurityCode:
                  return
            
            advice = self._advisor(candle)
            if advice is None or advice.DateTime <= self._start:
                  return
            
            self._queue.put(advice)


class Strategy:
      def __init__(self,
            trader,
            portfolio: domaintypes.PortfolioInfo,
            security: domaintypes.SecurityInfo,
            amount: float,
            lever: float,
            maxLever: float,
            ):
            
            self._trader = trader
            self._portfolio = portfolio
            self._security = security
            self._amount = amount
            self._lever = lever
            self._maxLever = maxLever
                        
            initPosition = trader.getPosition(portfolio, security)
            logging.info(f"Init position {security.Name} {initPosition}")
            self._position = initPosition
            self._basePrice = None

      def onNewAdvice(self, advice: Advice):
            if self._security.Code != advice.SecurityCode:
                  return
            
            logging.debug(f"Advice changed {advice}")

            if self._basePrice is None:
                self._basePrice = advice.Price
                logging.debug(f"Init base price {self._security.Name} {advice.DateTime} {advice.Price}")

            leverPos = max(-self._maxLever, min(self._maxLever, advice.Position*self._lever))
            position = self._amount / (self._basePrice * self._security.Lever) * leverPos

            volume = int(position - self._position)
            if volume == 0:
                  return

            price = priceWithSlippage(advice.Price, volume)
            logging.info(f"Register order security={self._security.Name} price={price} volume={volume}")
            self._trader.registerOrder(domaintypes.Order(
                  Portfolio=self._portfolio,
                  Security=self._security,
                  Volume=volume,
                  Price=price,
            ))
            self._position += volume # считаем, что заявка исполнилась


def priceWithSlippage(price: float, volume: int)-> float:
	Slippage = 0.001
	if volume > 0:
		return price * (1 + Slippage)
	else:
		return price * (1 - Slippage)
