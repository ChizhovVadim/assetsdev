import argparse
import os
import sys
from dataclasses import dataclass
import datetime

from internal import xirr, candles
from . import storage, domaintypes

@dataclass
class BalanceEntry:
    VolumeStart: int
    VolumeFinish: int

#securityInfo будет нужен при учете сплита акций
def buildPnLReport(securityInfo: dict[str,domaintypes.SecurityInfo],
                   myTrades: list[domaintypes.MyTrade],
                   myDividends: list[domaintypes.DividendSchedule],
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
            amountStart += item.VolumeStart*candleStorage.candleByDate(secCode, startDate).C
        if item.VolumeFinish != 0:
            amountFinish += item.VolumeFinish*candleStorage.candleByDate(secCode, finishDate).C
    
    payments.append(xirr.Payment(startDate, -amountStart))
    payments.append(xirr.Payment(finishDate, amountFinish))

    PnL = amountFinish-amountStart+totalDividends-totalAddition

    rateInfo = xirr.calcRate(payments, rateType)

    benchmarkRate, benchmarkAnnualRate = calcBenchmark(candleStorage, startDate, finishDate)

    displayDateLayout = "%d.%m.%Y"

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

def calcBenchmark(candleStorage, startDate, finishDate):
    benchmarkTicker = "MCFTRR"
    benchmarkOpen = candleStorage.candleByDate(benchmarkTicker, startDate)
    benchmarkClose = candleStorage.candleByDate(benchmarkTicker, finishDate)

    benchmarkRate = benchmarkClose.C / benchmarkOpen.C
    benchmarkAnnualRate = pow(benchmarkRate, 1.0/xirr.yearsBetween(startDate, finishDate))
    return benchmarkRate, benchmarkAnnualRate

def pnlHandler(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', type=str, default="")
    parser.add_argument('--ratetype', type=str, default="arsagera")
    parser.add_argument('--start', type=datetime.datetime.fromisoformat)
    parser.add_argument('--finish', type=datetime.datetime.fromisoformat)
    args = parser.parse_args(argv)

    candleStorage = candles.CandleStorage(os.path.expanduser("~/TradingData/Portfolio"))
    securityInfo = storage.loadSecurityInfo(os.path.expanduser("~/Data/assets/StockSettings.xml"))
    myTrades = storage.loadMyTrades(os.path.expanduser("~/Data/assets/trades.csv"))
    myDividends = storage.loadMyDividends(os.path.expanduser("~/Data/assets/Dividends.xml"))
    buildPnLReport(securityInfo, myTrades, myDividends, candleStorage,
                                        args.account, args.start, args.finish, args.ratetype)

if __name__ == "__main__":
    pnlHandler(sys.argv[1:])
