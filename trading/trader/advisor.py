import logging

import candles
from trading.advisors import testAdvisor, Advisor
from .import domaintypes

def initAdvisor(
    config: domaintypes.StrategyConfig,
    security: domaintypes.SecurityInfo,
    canldeStorage: candles.CandleStorage,
    candleInterval: candles.CandleInterval,
    trader,
):
    initAdvice = None
    advisor = testAdvisor(config.Name)

    if canldeStorage is not None:
        for candle in canldeStorage.read(config.SecurityCode):
            advice = advisor(candle)
            if advice is not None:
                initAdvice = advice
        logging.debug(f"Init advice {initAdvice}")

    new_bars = trader.getLastCandles(security, candleInterval)
    if not new_bars:
        logging.warning("Quik candles empty")
    else:
        logging.info(f"Quik candles {len(new_bars)} {new_bars[0]} {new_bars[-1]}")
        for candle in new_bars:
            advice = advisor(candle)
            if advice is not None:
                initAdvice = advice

    logging.info(f"Init advice {initAdvice}")

    return filterCandleAdvisor(advisor, security.Code)

def filterCandleAdvisor(advisor: Advisor, secCode: str):
    def f(candle: candles.Candle):
        if candle.SecurityCode != secCode:
            return None
        return advisor(candle)
    return f
