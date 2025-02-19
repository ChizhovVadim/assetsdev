import argparse
import logging
import os
import datetime

import candles
from trading import settings
from trading import advisors

from .mocktrader import MockTrader
from .quiktrader import QuikTrader
from .storage import loadSettings
from .import forts
from .import domaintypes

today = datetime.datetime.today()

def traderHandler():
      parser = argparse.ArgumentParser()
      parser.add_argument('--client', type=str, required=True)
      args = parser.parse_args()

      # в питоне можно настройки хранить прямо в settings, но исторически храним в xml.
      traderSettings = loadSettings(settings.traderSettingsPath)

      client = next(
		(client for client in traderSettings.Clients if client.Key == args.client),
		None)
      if client is None:
            raise ValueError("Client not found", args.client)
    
      today = datetime.date.today()
      logPath = os.path.join(
            os.path.expanduser("~/TradingData/Logs/luatrader"),
            args.client,
            f"{today.strftime("%Y-%m-%d")}.txt")
      logging.basicConfig(
            format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
            level=logging.DEBUG,
            handlers=[logging.StreamHandler(), logging.FileHandler(logPath)])

      logging.info("Application started.")
    
      canldeStorage = candles.CandleStorage(settings.candlesPath, settings.defaultCandleInterval)

      trade(canldeStorage, client, traderSettings.StrategyConfigs)

class Strategy:
      def __init__(self,
                   canldeStorage: candles.CandleStorage,
                   config: domaintypes.StrategyConfig):
            
            secInfo = forts.getSecurityInfo(config.SecurityCode)
            advisor = advisors.testAdvisor(config.Name)

            initAdvice = None
            for candle in canldeStorage.read(config.SecurityCode):
                  advice = advisor(candle)
                  if advice is not None:
                        initAdvice = advice
            logging.info(f"Init advice {initAdvice}")

            self._security = secInfo
            self._advisor = advisor
            self._lastAdvice = initAdvice

      def onNewCadnle(self, candle: candles.Candle):
            if self._security.Code != candle.SecurityCode:
                  return
            advice = self._advisor(candle)
            if advice is None:
                  return
            if advice.DateTime >= today:
                  logging.info(f"Advice changed {advice}")
            self._lastAdvice = advice


def trade(canldeStorage: candles.CandleStorage,
          client: domaintypes.Client,
          strategyConfigs: list[domaintypes.StrategyConfig]):
      
      strategies = []
      for config in strategyConfigs:
            strategies.append(Strategy(canldeStorage, config))

      def onNewCandle(candle):
            for strategy in strategies:
                  strategy.onNewCadnle(candle)
      
      trader = MockTrader()
      #trader = QuikTrader(client.Port)
      try:
            if not trader.IsConnected():
                  raise RuntimeError("quik is not connected")
            
            portfolio = domaintypes.PortfolioInfo(Firm=client.Firm, Portfolio=client.Portfolio)
            startAmount = trader.IncomingAmount(portfolio)
            availableAmount = _calcAvailableAmount(startAmount, client)
            logging.info(f"Init portfolio amount {startAmount} availableAmount {availableAmount}")

            #quik.OnNewCandle = onNewCandle            
            for strategy in strategies:
                  new_bars = trader.GetLastCandles(strategy._security, settings.defaultCandleInterval)
                  if not new_bars:
                        logging.warning("Quik candles empty")
                  else:
                        logging.info(f"Quik candles {len(new_bars)} {new_bars[0]} {new_bars[-1]}")
                        for candle in new_bars:
                              strategy.onNewCadnle(candle)
                        logging.info(f"Init advice with quik candles {strategy._lastAdvice}")

                  logging.debug(f"SubscribeToCandles {strategy._security.Name}")
                  trader.SubscribeCandles(strategy._security, settings.defaultCandleInterval)

            input("Enter - выход\n")
            #quik.UnsubscribeFromCandles
      finally:
            trader.Close()

def _calcAvailableAmount(amount: float, client: domaintypes.Client)-> float:
	if client.Amount:
		amount = client.Amount
	if client.MaxAmount:
		amount = min(amount, client.MaxAmount)
	if client.Weight:
		amount *= client.Weight
	return amount

traderHandler()
