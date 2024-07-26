from dataclasses import dataclass
import datetime
import argparse
import sys

from . import storage, domaintypes, settings
from internal import candles

@dataclass
class BalanceEntry:
    securityCode: str
    price: float
    volume: int
    amount: float
    weight: float

@dataclass
class BalanceReport:
    date: datetime.datetime
    account: str
    items: list[BalanceEntry]
    totalAmount: float

def buildBalanceReport(myTrades: list[domaintypes.MyTrade],
                       candleStorage: candles.CandleStorage, 
                       securityInfo: dict[str,domaintypes.SecurityInfo], 
                       account: str, 
                       date: datetime.datetime):
    volumes = {}
    for t in myTrades:
        if account != "" and t.Account != account: continue
        if t.ExecutionDate > date: continue
        volumes[t.SecurityCode] = volumes.get(t.SecurityCode, 0)+t.Volume
    totalAmount = 0.0
    items = []
    for securityCode, volume in volumes.items():
        if volume==0: continue
        price = candleStorage.candleByDate(securityCode, date).C
        amount = price*volume
        title = securityInfo[securityCode].Title
        items.append(BalanceEntry(title, price, volume, amount, 0.0))
        totalAmount += amount
    for entry in items:
        entry.weight = entry.amount/totalAmount
    items.sort(key=lambda x:x.amount, reverse=True)
    return BalanceReport(date, account, items, totalAmount)

def printReport(report: BalanceReport):
    print(f"Балансовый отчет по брокерскому счету '{report.account}' на дату {report.date.strftime(settings.displayDateLayout)}")
    print(f"СЧА {report.totalAmount:,.0f}")

    print(f"{'Наименование':<12} {'Цена':>10} {'Кол-во':>10} {'Стоимость':>10} {'Вес':>6}")
    for entry in report.items:
        print(f"{entry.securityCode:<12} {entry.price:>10} {entry.volume:>10,} {entry.amount:>10,.0f} {entry.weight*100:>6,.1f}")
    print()

def balanceHandler(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', type=str, default="")
    parser.add_argument('--date', type=datetime.datetime.fromisoformat, default=datetime.datetime.today())
    args = parser.parse_args(argv)
    
    candleStorage = candles.CandleStorage(settings.candlesPath)
    securityInfo = storage.loadSecurityInfo(settings.securityInfoPath)
    myTrades = storage.loadMyTrades(settings.myTradesPath)
    printReport(buildBalanceReport(myTrades, candleStorage, securityInfo, args.account, args.date))

if __name__ == "__main__":
    balanceHandler(sys.argv[1:])
