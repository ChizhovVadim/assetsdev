import argparse
import datetime
import logging
import time
import multiprocessing
from collections.abc import Callable

import candles

from trading import advisors
from . import moex
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
    parser.add_argument('--single', action="store_true")
    #TODO endquarter
    #TODO slippage
    args = parser.parse_args()
    candleInterval = candles.CandleInterval(args.timeframe)

    DEFAULT_SLIPPAGE = ((0.00462+0.00154)*2 + 0.01) * 0.01

    candleStorage = candles.CandleStorage(settings.candlesPath, candleInterval)
    advisorReport(candleStorage, args.advisor, args.security, args.lever, DEFAULT_SLIPPAGE,
                  args.startyear, args.startquarter, 2025, 0, args.single)

def advisorReport(
    candleStorage: candles.CandleStorage,
    advisorName: str,
    securityName: str,
    lever: float,
    slippage: float,
    startyear: int,
    startQuarter: int,
    finishYear: int,
    finishQuarter: int,
    singleContract: bool,
):
    if singleContract:
        tickers = [securityName]
    else:
        tickers = moex.quarterSecurityCodes(
            securityName, moex.TimeRange(startyear, startQuarter, finishYear, finishQuarter))
        
    hprs = multiContractHprs(advisorName, candleStorage, tickers, slippage, dateutils.afterLongHoliday)
    lever = lever or optimalLever(hprs, limitStdev(0.045))
    hprs = applyLever(hprs, lever)
    stat = statistic.computeHprStatistcs(hprs)

    print(f"Отчет {advisorName} {securityName}")
    print(f"Плечо {lever:.1f}")
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
