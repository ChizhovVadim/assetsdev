import logging
import argparse

import candles

from trading import settings
from trading import advisors

def statusHandler():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, required=True)
    parser.add_argument('--timeframe', type=str, default=settings.defaultCandleInterval)
    parser.add_argument('--security', type=str, required=True)
    args = parser.parse_args()
    candleInterval = candles.CandleInterval(args.timeframe)

    candleStorage = candles.CandleStorage(settings.candlesPath, candleInterval)

    viewStatus(candleStorage, args.security, advisors.testAdvisor(args.advisor))

def viewStatus(
    candleStorage: candles.CandleStorage,
    securityCode: str,
    advisor,
):
    advices = []
    for candle in candleStorage.read(securityCode):
        advice = advisor(candle)
        if not advice:
            continue
        if len(advices) == 0 or advices[-1].Position != advice.Position:
            advices.append(advice)
    print(advices[-10:])

if __name__ == "__main__":
    statusHandler()
