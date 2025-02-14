import argparse
import datetime
import functools
import logging

import candles
from candles.update.seccode import loadSecurityCodes
from candles.update.candleprovider import newCandleProvider
from candles.update.update import updateGroup

from assets import settings
from assets import security
from assets.portfolio.holding import getHoldingTickers

from .checkprice import checkPriceChange

def updateHandler():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', type=str, required=True)
    parser.add_argument('--timeframe', type=str, default=candles.CandleInterval.DAILY)
    parser.add_argument('--security', type=str)
    args = parser.parse_args()
    candleInterval = candles.CandleInterval(args.timeframe)

    if args.security:
        secCodes = [args.security] #str(args.security).split(",")
    else:
        secCodes = getHoldingTickers()
        secCodes.append(settings.benchmarkSecCode)

    secInfo = loadSecurityCodes(settings.securityInfoPath)
    providers = [newCandleProvider(x, secInfo)
                  for x in str(args.provider).split(",")]

    candleStorage = candles.CandleStorage(settings.candlesPath, candleInterval)
    securityInfo = security.loadSecurityInfo(settings.securityInfoPath)

    updateGroup(candleInterval,
                providers,
                candleStorage,
                lambda _:datetime.datetime(year=2013, month=1, day=1),
                functools.partial(checkPriceChange, width=0.25, securityInfo=securityInfo),
                secCodes)

if __name__ == "__main__":
    updateHandler()
