from dataclasses import dataclass
import datetime

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

def buildBalanceReport(myTrades, candleStorage, securityInfo, account, date):
    if date is None:
        date = datetime.datetime.today()
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
    print(f"Балансовый отчет '{report.account}' на дату {report.date:%Y-%m-%d}")
    print(f"СЧА {report.totalAmount:,.0f}")

    for entry in report.items:
        print(f"{entry.securityCode:<12} {entry.price:>10} {entry.volume:>10,} {entry.amount:>10,.0f} {entry.weight*100:>4,.1f}")    
