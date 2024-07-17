import sys
import logging
import os
import argparse

from internal import candles
from . import domaintypes, storage

def holdingTickers(myTrades: list[domaintypes.MyTrade])->list[str]:
    d = {}
    for t in myTrades:
        d[t.SecurityCode] = d.get(t.SecurityCode, 0) + t.Volume
    return [k for k, v in d.items() if v != 0]

def updateHandler(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', type=str, required=True)
    args = parser.parse_args(argv)

    myTrades = storage.loadMyTrades(os.path.expanduser("~/Data/assets/trades.csv"))
    candleStorage = candles.CandleStorage(os.path.expanduser("~/TradingData/Portfolio"))
    securityInfo = storage.loadSecurityInfo(os.path.expanduser("~/Data/assets/StockSettings.xml"))

    tf = candles.Timeframe.DAILY
    # or providers="finam,mfd"?
    providerName = args.provider
    if providerName == "finam":
        finamCodes = { key: val.FinamCode for key, val in securityInfo.items() }
        provider = candles.FinamProvider(finamCodes, tf)
    elif providerName == "mfd":
        mfdCodes = { key: val.MfdCode for key, val in securityInfo.items() }
        provider = candles.MfdProvider(mfdCodes, tf)
    else:
        raise ValueError("wrong provider", providerName)
    candleUpdateService = candles.CandleUpdateService(provider, candleStorage)
    tickers = holdingTickers(myTrades)
    BenchmarkIndex = "MCFTRR"
    tickers.append(BenchmarkIndex)
    candleUpdateService.updateGroup(tickers)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    updateHandler(sys.argv[1:])
