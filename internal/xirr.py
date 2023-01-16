from dataclasses import dataclass
import datetime
import math

@dataclass(frozen=True)
class Payment:
    Date: datetime.datetime
    Sum: float

# https://www.youtube.com/watch?v=9_Lj1CSbAh0&t=497s
def arsageraRate(payments: list[Payment]):
    payments = sorted(payments, key=lambda x: x.Date)
    minDate = payments[0].Date
    maxDate = payments[-1].Date
    totalYears = yearsBetween(minDate, maxDate)

    workingAmount=0.0
    workingSum=0.0
    totalPnL=0.0
    for i, item in enumerate(payments):
        current = item.Sum
        totalPnL += current
        if i < len(payments)-1:
            workingSum -= current
            if workingSum > 0:
                weight = yearsBetween(item.Date, payments[i+1].Date) / totalYears
                workingAmount += workingSum * weight

    rate = 1+totalPnL/workingAmount
    annualRate = rate ** (1.0/totalYears)
    return rate, annualRate

def yearsBetween(minDate, maxDate):
    return (maxDate-minDate).days/365.25

@dataclass(frozen=True)
class Cashflow:
    Years: float
    Sum: float

def _convertToCashflows(payments: list[Payment]):
    minDate = min(payments, key= lambda x: x.Date).Date
    return [Cashflow(yearsBetween(minDate, x.Date), x.Sum) for x in payments]

def irr(payments):
    return _calculateXirr(_convertToCashflows(payments), 0.01, 1000000, 0.0001)

def _calculateXirr(cashFlows, lowRate, highRate, precision):
    lowResult = _calcEquation(cashFlows, lowRate)
    highResult = _calcEquation(cashFlows, highRate)
    while True:
        if math.copysign(1.0, lowResult)==math.copysign(1.0, highResult):
            return None
        
        middleRate = 0.5 * (lowRate + highRate)
        middleResult = _calcEquation(cashFlows, middleRate)
        if abs(middleResult) <= precision:
            return middleRate

        if math.copysign(1.0, middleResult) == math.copysign(1.0, lowResult):
            lowRate = middleRate
            lowResult = middleResult
        else:
            highRate = middleRate
            highResult = middleResult


def _calcEquation(cashflows, rate):
    return sum(x.Sum * pow(rate, -x.Years) for x in cashflows)
