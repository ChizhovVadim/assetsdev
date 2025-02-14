from typing import NamedTuple
import datetime
import math
import enum

class Payment(NamedTuple):
    Date: datetime.datetime
    Sum: float

class RateInfo(NamedTuple):
	StartDate: datetime.datetime
	FinishDate: datetime.datetime
	Years: float
	Rate: float
	AnnualRate: float

class RateType(enum.StrEnum):
    IRR = "irr"
    ARSAGERA = "arsagera"

def calcRate(payments: list[Payment], type: str)-> RateInfo:
    "По заданным платежам вычисляет внутреннюю норму доходности"
    
    if type == "arsagera":
        return arsageraRate(payments)
    elif type == "irr":
        return irr(payments)
    else:
        raise ValueError(f"bad ratetype {type}")

# https://www.youtube.com/watch?v=9_Lj1CSbAh0&t=497s
def arsageraRate(payments: list[Payment])-> RateInfo:
    payments = sorted(payments, key=lambda x: x.Date)
    if payments[0].Sum == 0:
        raise ValueError("zero payment", payments[0])
    if payments[-1].Sum == 0:
        raise ValueError("zero payment", payments[-1])
    
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
    return RateInfo(
        StartDate=minDate,
	    FinishDate=maxDate,
	    Years=totalYears,
	    Rate=rate,
	    AnnualRate=annualRate,
    )

def yearsBetween(minDate, maxDate):
    return (maxDate-minDate).days/365.25

class Cashflow(NamedTuple):
    Years: float
    Sum: float

def _convertToCashflows(payments: list[Payment]):
    minDate = min(payments, key= lambda x: x.Date).Date
    return [Cashflow(yearsBetween(minDate, x.Date), x.Sum) for x in payments]

def irr(payments: list[Payment])-> RateInfo:
    firstPayment = min(payments, key= lambda x: x.Date)
    lastPayment = max(payments, key= lambda x: x.Date)
    if firstPayment.Sum == 0:
        raise ValueError("zero payment", firstPayment)
    if lastPayment.Sum == 0:
        raise ValueError("zero payment", lastPayment)

    minDate = firstPayment.Date
    maxDate = lastPayment.Date

    totalYears = yearsBetween(minDate, maxDate)
    cashflows = _convertToCashflows(payments)
    annualRate = _calculateXirr(cashflows, 1e-6, 1e6, 1e-4)
    rate = pow(annualRate, totalYears)
    return RateInfo(
        StartDate=minDate,
	    FinishDate=maxDate,
	    Years=totalYears,
	    Rate=rate,
	    AnnualRate=annualRate,
    )

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
