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
from .strategy import Strategy
from .import forts
from .import domaintypes

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

def trade(canldeStorage: candles.CandleStorage,
          client: domaintypes.Client,
          strategyConfigs: list[domaintypes.StrategyConfig]):
      
      start = datetime.datetime.today()+datetime.timedelta(minutes=-10)
      
      #trader = MockTrader()
      trader = QuikTrader(client.Port)
      try:
            if not trader.isConnected():
                  raise RuntimeError("quik is not connected")
            
            portfolio = domaintypes.PortfolioInfo(Firm=client.Firm, Portfolio=client.Portfolio)
            startAmount = trader.incomingAmount(portfolio)
            availableAmount = _calcAvailableAmount(startAmount, client)
            logging.info(f"Init portfolio amount {startAmount} availableAmount {availableAmount}")
            if availableAmount == 0:
                  logging.warning("availableAmount zero")

            strategies = []
            for config in strategyConfigs:
                  strategy = Strategy(
                        advisor=advisors.testAdvisor(config.Name),
                        security=forts.getSecurityInfo(config.SecurityCode),
                        amount=availableAmount,
                        lever=config.Lever*config.Weight,
                        maxLever=config.MaxLever*config.Weight,
                        start=start,
                  )
                  strategy.initCandles(canldeStorage.read(config.SecurityCode))
                  strategies.append(strategy)

            for strategy in strategies:
                  new_bars = trader.getLastCandles(strategy._security, settings.defaultCandleInterval)
                  if not new_bars:
                        logging.warning("Quik candles empty")
                  else:
                        logging.info(f"Quik candles {len(new_bars)} {new_bars[0]} {new_bars[-1]}")
                        strategy.initCandles(new_bars)

            def onNewCandle(candle: candles.Candle):
                  for strategy in strategies:
                        strategy.onNewCandle(candle)

            trader.setNewCandleCallback(onNewCandle)
            for strategy in strategies:
                  logging.debug(f"SubscribeToCandles {strategy._security.Name}")
                  trader.subscribeCandles(strategy._security, settings.defaultCandleInterval)

            input("Enter - выход\n")
            #quik.UnsubscribeFromCandles
      finally:
            trader.close()

def _calcAvailableAmount(amount: float, client: domaintypes.Client)-> float:
	if client.Amount:
		amount = client.Amount
	if client.MaxAmount:
		amount = min(amount, client.MaxAmount)
	if client.Weight:
		amount *= client.Weight
	return amount

traderHandler()
