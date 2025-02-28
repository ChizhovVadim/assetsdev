import datetime
import itertools
from collections.abc import Sequence, Callable

from candles import Candle
from trading.advisors import Advice
from trading import dateutils
from .datesum import DateSum

def calcDailyPeriodResults(
        advisor: Callable[[Candle], Advice],
        candles: Sequence[Candle],
        slippage: float,
        skipPnl:  Callable[[datetime.datetime, datetime.datetime], bool],
) -> list[DateSum]:
	"По советнику на исторических барах вычисляет дневные доходности"

	res = []
	pnl = 0.0
	baseAdvice = None
	lastAdvice = None

	for candle in candles:
		advice = advisor(candle)
		if advice is None:
			continue

		if baseAdvice is None:
			baseAdvice=advice
			lastAdvice=advice
			continue

		#TODO проверить, что skipPnl и новый день согласованы.
		if dateutils.isNewFortsDateStarted(lastAdvice.DateTime, advice.DateTime):
			res.append(DateSum(lastAdvice.DateTime.date(), 1 + pnl/baseAdvice.Price))
			pnl = 0.0
			baseAdvice=lastAdvice
		if not skipPnl(lastAdvice.DateTime, advice.DateTime):
			pnl += (lastAdvice.Position*(advice.Price-lastAdvice.Price) -
            slippage*advice.Price*abs(advice.Position-lastAdvice.Position))
		lastAdvice = advice

	if lastAdvice is not None:
		res.append(DateSum(lastAdvice.DateTime.date(), 1 + pnl/baseAdvice.Price))

	return res

def concatHprs(hprByContract: list[list[DateSum]])->list[DateSum]:
	"Объединияет дневные доходности по разным контрактам"
	
	res = []
	for hprs in hprByContract:
		if not hprs:
			continue
		if res:
			# последний день предыдущего контракта может быть не полный
			res.pop()
		if res:
			lastDate = res[-1].Date
			# or x.Date<lastDate
			res.extend(itertools.dropwhile(lambda x: x.Date <= lastDate, hprs))
		else:
			res.extend(hprs)
	return res
