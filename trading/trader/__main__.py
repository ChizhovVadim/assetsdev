import argparse
import logging
import os
import datetime
import queue

import candles
from trading import settings

from .mocktrader import MockTrader
from .quiktrader import QuikTrader
from .storage import loadSettings
from .advisor import initAdvisor
from .strategy import initStrategy
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

            adviceQueue = queue.Queue()

            advisors = []
            strategies = []
            for config in strategyConfigs:
                  security=forts.getSecurityInfo(config.SecurityCode)

                  advisor = initAdvisor(config, security, canldeStorage, settings.defaultCandleInterval, trader)
                  advisors.append(advisor)

                  strategy = initStrategy(trader, portfolio, security, availableAmount, config)
                  strategies.append(strategy)

            def onNewCandle(candle: candles.Candle):
                  for advisor in advisors:
                        advice = advisor(candle)
                        if advice is not None and advice.DateTime >= start:
                              logging.debug(f"Advice changed {advice}")
                              if adviceQueue is not None:
                                    adviceQueue.put(advice)

            trader.setNewCandleCallback(onNewCandle)
            for strategy in strategies:
                  logging.debug(f"SubscribeToCandles {strategy._security.Name}")
                  # WARN Подписываемся, но читать еще не начали
                  trader.subscribeCandles(strategy._security, settings.defaultCandleInterval)

            while True:
                  advice = adviceQueue.get()
                  for strategy in strategies:
                        strategy.onNewAdvice(advice)
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
