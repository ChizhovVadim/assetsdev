import sys
import argparse
import logging
import functools
import math
import datetime

from internal import candles
import trading.storage
import trading.settings
import internal.candles.finam
import internal.candles.mfd

def updateHandler(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument('--provider', type=str)
	parser.add_argument('--security', type=str)
	args = parser.parse_args(argv)
	providerName = args.provider

	strategySettings = trading.storage.loadStrategySettings(trading.settings.strategySettingsPath)
	tf = candles.Timeframe.MINUTES5
	providers = []

	if providerName is None or providerName == "mfd":
		mfdCodes = { secCode.Code: secCode.MfdCode
				for secCode in strategySettings.SecurityCodes
				if secCode.MfdCode }
		mfdProvider = functools.partial(internal.candles.mfd.load, timeFrame=tf, secCodes=mfdCodes)
		providers.append(mfdProvider)

	if providerName is None or providerName == "finam":
		finamCodes = { secCode.Code: secCode.FinamCode
				for secCode in strategySettings.SecurityCodes
				if secCode.FinamCode }
		finamProvider = functools.partial(internal.candles.finam.load, timeFrame=tf, secCodes=finamCodes)
		providers.append(finamProvider)

	canldeStorage = candles.CandleStorage(trading.settings.candlesPath)
	if args.security:
		tickers = [args.security]
	else:
		tickers = [ conf.SecurityCode for conf in strategySettings.StrategyConfigs ]
	candles.updateGroup(providers, canldeStorage, calcStartDate, checkPriceChange, tickers)

def checkPriceChange(securityCode: str, x: candles.Candle, y: candles.Candle):
    closeChange = abs(math.log(x.C/y.C))
    openChange = abs(math.log(x.C/y.O))
    width = 0.25
    if not(openChange >= width and closeChange >= width):
        return
    raise ValueError("big jump", securityCode, x, y)

def approxExpirationDate(securityCode: str)-> datetime.datetime:
	# С 1 июля 2015, для новых серий по кот нет открытых позиций, все основные фьючерсы и опционы должны исполняться в 3-й четверг месяца
	# name-month.year
	delim1 = securityCode.index("-")
	delim2 = securityCode.index(".")
	month = int(securityCode[delim1+1:delim2])
	curYear = datetime.datetime.today().year
	year = int(securityCode[delim2+1:])+curYear-curYear%100
	return datetime.datetime(year, month, 15)

# expdate-4month
def calcStartDate(securityCode: str)-> datetime.datetime:
	return approxExpirationDate(securityCode)+datetime.timedelta(days=-4*30)

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	updateHandler(sys.argv[1:])
