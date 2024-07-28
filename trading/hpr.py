from collections.abc import Sequence
import functools
import statistics
import math

from trading.domaintypes import Advice, DateSum
from . import dateutils

def applyLever(hprs: list[DateSum], lever: float)->list[DateSum]:
	return [DateSum(hpr.DateTime, 1+lever*(hpr.Sum-1)) for hpr in hprs]

def limitStdev(stdev: float):
    def f(hprs: list[DateSum])-> bool:
        nonlocal stdev
        return statistics.stdev((math.log(x.Sum) for x in hprs)) < stdev
    return f

def optimalLever(hprs: list[DateSum], riskSpecification)-> float:
     minHpr = min(x.Sum for x in hprs)
     maxLever = 1.0/(1.0-minHpr)
     bestHpr = 1.0
     bestLever = 0.0
     for ratio in range(1, 100):
          lever = maxLever*ratio/100.0
          leverHprs = applyLever(hprs, lever)
          if riskSpecification and not riskSpecification(leverHprs):
               break
          hpr = functools.reduce(lambda x,y:x*y.Sum, leverHprs, 1.0)
          if hpr < bestHpr:
               break
          bestHpr = hpr
          bestLever = lever
     return bestLever

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
