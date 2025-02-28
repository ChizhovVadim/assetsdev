import argparse
from dataclasses import dataclass
import datetime

import xirr
import candles

from assets import settings
from assets import security

from .domaintypes import MyTrade
from .storage import loadMyTrades

@dataclass
class BalanceEntry:
    VolumeStart: int
    VolumeFinish: int

# TODO нужно согласованно использовать сравнение дат строгое не строгое и startDate.
# Брать по умолчанию последний день предыдущего года?
def buildPnLReport(securityInfo: dict[str,security.SecurityInfo],
                   myTrades: list[MyTrade],
                   myDividends: list[security.DividendSchedule],
                   candleStorage: candles.CandleStorage,
                   account: str,
                   startDate: datetime.datetime,
                   finishDate: datetime.datetime,
                   rateType: str):
    today = datetime.datetime.today()
    if startDate is None:
        startDate = datetime.datetime(today.year, 1, 1)
    if finishDate is None:
        finishDate = today
    if startDate>finishDate:
        raise ValueError("startDate>finishDate")

    payments = []

    totalDividends = 0.0
    for d in myDividends:
        for rd in d.Received:
            if not((account=="" or rd.Account==account)and
                startDate<rd.Date<=finishDate): continue
            totalDividends += rd.Sum
            payments.append(xirr.Payment(rd.Date, rd.Sum))

    totalCommission = 0.0
    totalAddition = 0.0
    balanceItems = {}
    for t in myTrades:
        if account and t.Account!=account: continue
        if not(t.ExecutionDate<=finishDate): continue

        if t.SecurityCode not in balanceItems:
            balanceItems[t.SecurityCode]=BalanceEntry(0, 0)

        balanceItems[t.SecurityCode].VolumeFinish += t.Volume
        
        if not(startDate<t.ExecutionDate):
            balanceItems[t.SecurityCode].VolumeStart += t.Volume
            continue

        commission = t.ExchangeComission + t.BrokerComission
        totalCommission += commission
        amount = t.Volume*t.Price+commission
        totalAddition += amount
        payments.append(xirr.Payment(t.ExecutionDate, -amount))
    
    amountStart = 0.0
    amountFinish = 0.0
    for secCode, item in balanceItems.items():
        if item.VolumeStart != 0:
            amountStart += item.VolumeStart*candleStorage.candleByDate(secCode, startDate).ClosePrice
        if item.VolumeFinish != 0:
            amountFinish += item.VolumeFinish*candleStorage.candleByDate(secCode, finishDate).ClosePrice
    
    ## Проверки на 0 нужны?
    if amountStart:
        payments.append(xirr.Payment(startDate, -amountStart))
    if amountFinish:
        payments.append(xirr.Payment(finishDate, amountFinish))

    PnL = amountFinish-amountStart+totalDividends-totalAddition

    rateInfo = xirr.calcRate(payments, rateType)

    benchmarkRate, benchmarkAnnualRate = calcBenchmark(candleStorage, startDate, finishDate)

    displayDateLayout = settings.displayDateLayout

    print(f"Отчет о прибылях/убытках по брокерскому счету '{account}'")
    print(f"с '{startDate.strftime(displayDateLayout)}' по '{finishDate.strftime(displayDateLayout)}', {rateInfo.Years:.1f} лет")
    print(f"СЧА на начало периода {amountStart:,.0f}")
    print(f"СЧА на конец периода {amountFinish:,.0f}")
    print(f"Инвестировано новых средств {totalAddition:,.0f}")
    print(f"Дивиденды {totalDividends:,.0f}")
    print(f"Комиссия {totalCommission:,.0f}")
    print(f"Прибыль {PnL:,.0f}")
    print(f"Прибыль {(rateInfo.Rate-1)*100:.1f}%")
    print(f"Прибыль {(rateInfo.AnnualRate-1)*100:.1f}% годовых ({rateType})")
    print(f"Бенчмарк {(benchmarkRate-1)*100:.1f}%")
    print(f"Бенчмарк {(benchmarkAnnualRate-1)*100:.1f}% годовых")
    print()

def calcBenchmark(candleStorage: candles.CandleStorage, 
                  startDate: datetime.datetime, 
                  finishDate: datetime.datetime):
    benchmarkTicker = settings.benchmarkSecCode
    benchmarkOpen = candleStorage.candleByDate(benchmarkTicker, startDate)
    benchmarkClose = candleStorage.candleByDate(benchmarkTicker, finishDate)

    benchmarkRate = benchmarkClose.ClosePrice / benchmarkOpen.ClosePrice
    benchmarkAnnualRate = pow(benchmarkRate, 1.0/xirr.yearsBetween(startDate, finishDate))
    return benchmarkRate, benchmarkAnnualRate

def pnlHandler():
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', type=str, default="")
    parser.add_argument('--ratetype', type=str, default="arsagera")
    parser.add_argument('--start', type=datetime.datetime.fromisoformat)
    parser.add_argument('--finish', type=datetime.datetime.fromisoformat)
    args = parser.parse_args()

    candleStorage = candles.CandleStorage(settings.candlesPath, candles.CandleInterval.DAILY)
    securityInfo = security.loadSecurityInfo(settings.securityInfoPath)
    myTrades = loadMyTrades(settings.myTradesPath)
    myDividends = security.loadMyDividends(settings.myDividendsPath)
    buildPnLReport(securityInfo, myTrades, myDividends, candleStorage,
                                        args.account, args.start, args.finish, args.ratetype)

if __name__ == "__main__":
    pnlHandler()
