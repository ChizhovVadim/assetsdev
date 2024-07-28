import sys
import argparse
import logging
import time
import itertools
import multiprocessing
from typing import NamedTuple

from trading import advisor, hpr, statistic, settings, dateutils, domaintypes
from internal import candles

class TimeRange(NamedTuple):
	StartYear:     int
	StartQuarter:  int
	FinishYear:    int
	FinishQuarter: int

def buildAdvisor():
	res = advisor.may24Advisor(0.006)
	res = advisor.applyCandleValidation(res)
	return res

def historyHandler(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument('--security', type=str, default="CNY")
	parser.add_argument('--startyear', type=int, default=2022)
	parser.add_argument('--startquarter', type=int, default=2)
	parser.add_argument('--lever', type=float)
	args = parser.parse_args(argv)
	print(args)

	tr = TimeRange(
		StartYear=args.startyear,
		StartQuarter=args.startquarter,
		FinishYear=2024,
		FinishQuarter=2,
	)
	tickers = quarterSecurityCodes(args.security, tr)
	candleStorage = candles.CandleStorage(settings.candlesPath)

	hprs = multiContractHprs(candleStorage, tickers, 0.0002, dateutils.afterLongHoliday)
	lever = args.lever if args.lever else hpr.optimalLever(hprs, hpr.limitStdev(0.045))
	print(f"Плечо {lever:.1f}")
	hprs = hpr.applyLever(hprs, lever)

	stat = statistic.computeHprStatistcs(hprs)
	statistic.printReport(stat)

def quarterSecurityCodes(name: str, tr: TimeRange)-> list[str]:
	res = []
	for year in range(tr.StartYear, tr.FinishYear+1):
		for quarter in range(0, 4):
			if year == tr.StartYear:
				if quarter<tr.StartQuarter:
					continue
			if year == tr.FinishYear:
				if quarter>tr.FinishQuarter:
					break
			res.append(f"{name}-{3+quarter*3}.{year%100:02}")
	return res

def contractHprs(args)->list[domaintypes.DateSum]:
	(candleStorage,secCode,slippage,skipPnl) = args
	advisor = buildAdvisor()
	advices = (advice for candle in candleStorage.read(secCode)
		if (advice := advisor(candle)) is not None)
	return hpr.calcHprs(advices, slippage=slippage, skipPnl=skipPnl)

def multiContractHprs(
	candleStorage,
	secCodes,
	slippage,
	skipPnl,
	)->list[domaintypes.DateSum]:

	hprByContract = []
	with multiprocessing.Pool() as pool:
		args = ((candleStorage, secCode, slippage, skipPnl) for secCode in secCodes)
		for hprs in pool.map(contractHprs, args):
			hprByContract.append(hprs)
	return concatHprs(hprByContract)

def concatHprs(hprByContract)->list[domaintypes.DateSum]:
	res = []
	for hprs in hprByContract:
		if not hprs:
			continue
		if res:
			# последний день предыдущего контракта может быть не полный
			res.pop()
		if res:
			lastDate = res[-1].DateTime
			# or x.DateTime.date()<lastDate.date()
			res.extend(itertools.dropwhile(lambda x: x.DateTime <= lastDate, hprs))
		else:
			res.extend(hprs)
	return res

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	start = time.time()
	historyHandler(sys.argv[1:])
	print(f"Elapsed: {(time.time()-start):.2f}")
