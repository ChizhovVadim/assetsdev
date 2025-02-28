import logging
import datetime

from trading.advisors import Advice
from .import domaintypes

def initStrategy(
      trader,
      portfolio: domaintypes.PortfolioInfo,
      security: domaintypes.SecurityInfo,
      amount: float,
      config: domaintypes.StrategyConfig,
):
      initPosition = trader.getPosition(portfolio, security)
      logging.info(f"Init position {security.Name} {initPosition}")
      
      return Strategy(trader, portfolio, security, amount,
                      config.Lever*config.Weight,
                      config.MaxLever*config.Weight,
                      initPosition)

class Strategy:
      def __init__(self,
            trader,
            portfolio: domaintypes.PortfolioInfo,
            security: domaintypes.SecurityInfo,
            amount: float,
            lever: float,
            maxLever: float,
            initPosition: int,
            ):
            
            self._trader = trader
            self._portfolio = portfolio
            self._security = security
            self._amount = amount
            self._lever = lever
            self._maxLever = maxLever
            self._position = initPosition
            self._basePrice = None

      def onNewAdvice(self, advice: Advice):
            # считаем, что сигнал слишком старый
            if (self._security.Code != advice.SecurityCode or
                  datetime.datetime.now() - advice.DateTime >= datetime.timedelta(minutes=9)):
                  return

            if self._basePrice is None:
                self._basePrice = advice.Price
                logging.debug(f"Init base price {self._security.Name} {advice.DateTime} {advice.Price}")

            leverPos = max(-self._maxLever, min(self._maxLever, advice.Position*self._lever))
            position = self._amount / (self._basePrice * self._security.Lever) * leverPos

            volume = int(position - self._position)
            if volume == 0:
                  return
            
            logging.info(f"New advice {advice}")

            if not self.checkPosition():
                  return

            price = priceWithSlippage(advice.Price, volume)
            logging.info(f"Register order security={self._security.Name} price={price} volume={volume}")
            # TODO try/except
            self._trader.registerOrder(domaintypes.Order(
                  Portfolio=self._portfolio,
                  Security=self._security,
                  Volume=volume,
                  Price=price,
            ))
            self._position += volume # считаем, что заявка исполнилась

      def checkPosition(self)-> bool:
            traderPos = int(self._trader.getPosition(self._portfolio, self._security))
            if self._position == traderPos:
                  logging.info(f"Check position {traderPos} +")
                  return True
            else:
                  logging.warning(f"Check position {self._position} {traderPos} !")
                  return False


def priceWithSlippage(price: float, volume: int)-> float:
	Slippage = 0.001
	if volume > 0:
		return price * (1 + Slippage)
	else:
		return price * (1 - Slippage)
