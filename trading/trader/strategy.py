import logging
import datetime

import candles
from .import domaintypes

class Strategy:
      def __init__(self,
            advisor,
            security: domaintypes.SecurityInfo,
            amount: float,
            lever: float,
            maxLever: float,
            start: datetime.datetime,
            ):
            
            self._advisor = advisor
            self._security = security
            self._amount = amount
            self._lever = lever
            self._maxLever = maxLever
            self._start = start
            
            self._basePrice = None
            self._lastAdvice = None

      def initCandles(self, candles):
            initAdvice = None
            for candle in candles:
                  advice = self._advisor(candle)
                  if advice is not None:
                        initAdvice = advice
            logging.info(f"Init advice {initAdvice}")

      def onNewCandle(self, candle: candles.Candle)->bool:
            if self._security.Code != candle.SecurityCode:
                  return False
            
            advice = self._advisor(candle)
            if advice is None or advice.DateTime <= self._start:
                  return False

            if self._basePrice is None:
                self._basePrice = advice.Price
                logging.debug(f"Init base price {advice.SecurityCode} {advice.DateTime} {advice.Price}")

            leverPos = max(-self._maxLever, min(self._maxLever, advice.Position*self._lever))
            quantity = self._amount / (self._basePrice * self._security.Lever) * leverPos

            self._lastAdvice = advice._replace(Position = quantity,
                                               Details = ("quantityAdvisor", advice.Position, advice.Details))
            logging.debug(f"Advice changed {self._lastAdvice}")
            return True
