import sys
import logging
import argparse
import math
import functools
import datetime

from internal import candles
import internal.candles.finam
import internal.candles.mfd
from . import domaintypes, storage, settings

def holdingTickers(myTrades: list[domaintypes.MyTrade])->list[str]:
    d = {}
    for t in myTrades:
        d[t.SecurityCode] = d.get(t.SecurityCode, 0) + t.Volume
    return [k for k, v in d.items() if v != 0]

def updateHandler(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', type=str)
    args = parser.parse_args(argv)
    providerName = args.provider

    myTrades = storage.loadMyTrades(settings.myTradesPath)
    candleStorage = candles.CandleStorage(settings.candlesPath)
    securityInfo = storage.loadSecurityInfo(settings.securityInfoPath)

    tf = candles.Timeframe.DAILY
    providers = []

    if providerName is None or providerName == "finam":
        finamCodes = { key: val.FinamCode for key, val in securityInfo.items() }
        finamProvider = functools.partial(internal.candles.finam.load, timeFrame=tf, secCodes=finamCodes)
        providers.append(finamProvider)

    if providerName is None or providerName == "mfd":
        mfdCodes = { key: val.MfdCode for key, val in securityInfo.items() }
        mfdProvider = functools.partial(internal.candles.mfd.load, timeFrame=tf, secCodes=mfdCodes)
        providers.append(mfdProvider)

    tickers = holdingTickers(myTrades)
    BenchmarkIndex = "MCFTRR"
    tickers.append(BenchmarkIndex)

    candles.updateGroup(providers,
                        candleStorage,
                        lambda _:datetime.datetime(year=2013, month=1, day=1),
                        functools.partial(checkPriceChange, securityInfo=securityInfo),
                        tickers)

def checkPriceChange(securityCode: str, x: candles.Candle, y: candles.Candle,
                     securityInfo: dict[str, domaintypes.SecurityInfo]):
    closeChange = abs(math.log(x.C/y.C))
    openChange = abs(math.log(x.C/y.O))
    width = 0.25
    if not(openChange >= width and closeChange >= width):
        return
    if securityInfo is not None:
        splits = securityInfo[securityCode].Splits
        for split in splits:
            if x.DateTime < split.Date < y.DateTime:
                logging.warning(f"split found {split}")
                return
    raise ValueError("big jump", securityCode, x, y)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    updateHandler(sys.argv[1:])
