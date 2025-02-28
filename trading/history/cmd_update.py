import argparse
import datetime
import functools
import logging
import math

import candles
from candles.update.seccode import loadFortsCodes
from candles.update.candleprovider import newCandleProvider
from candles.update.update import updateGroup

from trading import settings
from . import moex

def updateHandler():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', type=str, required=True)
    parser.add_argument('--timeframe', type=str, default=settings.defaultCandleInterval)
    parser.add_argument('--security', type=str, required=True)
    args = parser.parse_args()
    candleInterval = candles.CandleInterval(args.timeframe)

    secCodes = str(args.security).split(",")

    secInfo = loadFortsCodes(settings.fortsSecurityCodesPath)
    providers = [newCandleProvider(x, secInfo)
                  for x in str(args.provider).split(",")]

    candleStorage = candles.CandleStorage(settings.candlesPath, candleInterval)

    updateGroup(candleInterval,
                providers,
                candleStorage,
                caclFortsStartDate,
                functools.partial(checkPriceChange, width=0.25),
                secCodes)
    
# примерная дата экспирации минус 4 месяца
def caclFortsStartDate(secCode: str)-> datetime.datetime:
    expDate = moex.approxExpirationDate(secCode)
    if expDate is None:
        return None
    return expDate+datetime.timedelta(days=-4*30)

def checkPriceChange(securityCode: str,
                     x: candles.Candle,
                     y: candles.Candle,
                     width: float,
                     ):
    "Кидает ValueError, если большая разница цен x и y."
        
    closeChange = abs(math.log(x.ClosePrice / y.ClosePrice))
    openChange = abs(math.log(x.ClosePrice / y.OpenPrice))

    if not(openChange >= width and closeChange >= width):
        return

    raise ValueError("big jump", securityCode, x, y)

if __name__ == "__main__":
    updateHandler()
