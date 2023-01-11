from dataclasses import dataclass
import datetime

@dataclass(frozen=True)
class Payment:
    Date: datetime.datetime
    Sum: float

# https://www.youtube.com/watch?v=9_Lj1CSbAh0&t=497s
def ArsageraRate(payments: list[Payment]):
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
