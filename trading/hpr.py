from collections.abc import Sequence
from trading.domaintypes import Advice, DateSum
from . import dateutils

def applyLever(hprs, lever: float)->list[DateSum]:
	return [DateSum(hpr.DateTime, 1+lever*(hpr.Sum-1)) for hpr in hprs]

def calcHprs(advices: Sequence[Advice],
            slippage: float,
	        skipPnl)->list[DateSum]:
    res = []
    pnl = 0.0
    baseAdvice = None
    lastAdvice = None
    for advice in advices:
        if advice is None:
            continue
        if baseAdvice is None:
            baseAdvice=advice
            lastAdvice=advice
            continue
        if dateutils.isNewFortsDateStarted(lastAdvice.DateTime, advice.DateTime):
            res.append(DateSum(lastAdvice.DateTime, 1 + pnl/baseAdvice.Price))
            pnl = 0.0
            baseAdvice=lastAdvice
        if not skipPnl(lastAdvice.DateTime, advice.DateTime):
            pnl += (lastAdvice.Position*(advice.Price-lastAdvice.Price) -
            slippage*advice.Price*abs(advice.Position-lastAdvice.Position))
        lastAdvice = advice
    
    if lastAdvice is not None:
        res.append(DateSum(lastAdvice.DateTime, 1 + pnl/baseAdvice.Price))

    return res
