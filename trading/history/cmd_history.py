import argparse
import datetime
import logging
import time
import multiprocessing
from collections.abc import Callable

import candles

from trading import advisors
from trading import moex
from trading import settings
from trading import dateutils

from .import statistic
from .datesum import DateSum
from .lever import applyLever, optimalLever, limitStdev
from .hpr import calcDailyPeriodResults, concatHprs

def historyHandler():
    logging.basicConfig(level=logging.INFO)

    today = datetime.datetime.today()

    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, required=True)
    parser.add_argument('--timeframe', type=str, default=settings.defaultCandleInterval)
    parser.add_argument('--security', type=str, required=True)
    parser.add_argument('--startyear', type=int, default=today.year)
    parser.add_argument('--startquarter', type=int, default=0)
    parser.add_argument('--lever', type=float)
    #TODO endquarter
    #TODO slippage
    #TODO multy
    args = parser.parse_args()
    candleInterval = candles.CandleInterval(args.timeframe)

    candleStorage = candles.CandleStorage(settings.candlesPath, candleInterval)

    tickers = moex.quarterSecurityCodes(args.security, moex.TimeRange(args.startyear, args.startquarter, today.year, 0))
    hprs = multiContractHprs(args.advisor, candleStorage, tickers, 0.0002, dateutils.afterLongHoliday)

    lever = args.lever if args.lever else optimalLever(hprs, limitStdev(0.045))
    print(f"Плечо {lever:.1f}")
    hprs = applyLever(hprs, lever)
    stat = statistic.computeHprStatistcs(hprs)
    statistic.printReport(stat)

def singleContractHprs(args)->list[DateSum]:
    (advisorName,candleStorage,secCode,slippage,skipPnl) = args
    return calcDailyPeriodResults(
        advisors.testAdvisor(advisorName),
        candleStorage.read(secCode),
        slippage,
        skipPnl)

def multiContractHprs(
    advisorName: str,
	candleStorage: candles.CandleStorage,
	secCodes: list[str],
	slippage: float,
	skipPnl:  Callable[[datetime.datetime, datetime.datetime], bool],
    )->list[DateSum]:
    "Вычисляет дневные доходности советника по серии контрактов"
    
    parallel = True

    if parallel:
        hprByContract = []
        with multiprocessing.Pool() as pool:
            args = ((advisorName, candleStorage, secCode, slippage, skipPnl) for secCode in secCodes)
            for hprs in pool.map(singleContractHprs, args):
                hprByContract.append(hprs)
        return concatHprs(hprByContract)
    else:
        hprByContract = []
        for secCode in secCodes:
            args = (advisorName, candleStorage, secCode, slippage, skipPnl)
            hprByContract.append(singleContractHprs(args))
        return concatHprs(hprByContract)

if __name__ == "__main__":
    start = time.time()
    historyHandler()
    print(f"Elapsed: {(time.time()-start):.2f}")
