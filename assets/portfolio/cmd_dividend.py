import argparse
from dataclasses import dataclass
import datetime

from assets import settings
from assets import security

from .storage import loadMyTrades
from . import domaintypes

@dataclass
class DividendItem:
    Title: str
    RecordDate: datetime.datetime
    Rate: float
    Account: str
    Shares: int
    Expected: float
    PaymentDate: datetime.datetime
    Payment: float

def buildDividendReport(securityInfo: dict[str,security.SecurityInfo],
                        myTrades: list[domaintypes.MyTrade],
                        myDividends: list[security.DividendSchedule],
                        reportAccount: str,
                        year: int):
    if year is None:
        year = datetime.datetime.today().year
    
    items = []
    totalExpected = 0.0
    totalPayment = 0.0
    for d in myDividends:
        #if d.RecordDate.year != year: continue

        shares = _calculateShares(myTrades, d.FixDate, d.SecurityCode)

        title = securityInfo.get(d.SecurityCode).Title
        
        for account, volume in shares.items():
            if (reportAccount is not None) and account != reportAccount:
                continue
            if volume==0: continue
            expected = _calculateExpectedDividend(d.Rate, volume, d.FixDate)
            paymentDate, payment = _findPayment(d.Received, account)

            if paymentDate is None:
                 if d.RecordDate.year != year:
                      continue
            else:
                 if paymentDate.year != year:
                      continue

            items.append(DividendItem(title, d.FixDate, d.Rate, account, volume, expected, paymentDate, payment))

            totalExpected += expected
            totalPayment += payment

    items.sort(key=lambda x : x.RecordDate)
    toReceive=max(0, totalExpected-totalPayment)

    print(f"Отчет по дивидендам за '{year}' год")
    print(f"Ожидается {totalExpected:,.0f}")
    print(f"Получено {totalPayment:,.0f}")
    print(f"К получению {toReceive:,.0f}")
    print(f"{'Наименование':<12} {'Отсечка':<10} {'Дивиденд':>10} {'Счет':<7} {'Кол-во':>10} {'Ожидается':>10} {'Дата':<10} {'Получено':>10}")
    for item in items:
        print(f"{item.Title:<12} {dateStr(item.RecordDate)} {item.Rate:>10,} {item.Account:<7} {item.Shares:>10} {item.Expected:>10,.2f} {dateStr(item.PaymentDate):<10} {_format_zero(item.Payment,'>10,.2f')}")
    print()

def _format_zero(val,fmt):
    return format(val, fmt) if val else ""

def _calculateShares(myTrades, date, securityCode)->dict[str,int]:
    shares = {}
    for t in myTrades:
        if not(t.SecurityCode == securityCode and
            t.ExecutionDate <= date): continue
        shares[t.Account] = shares.get(t.Account, 0) + t.Volume
    return shares

def _calculateExpectedDividend(rate, shares, date):
    sum = round(rate*shares*100) / 100
    ndfl = round(sum * _dividendTaxRate(date))
    return round((sum-ndfl)*100) / 100

def _dividendTaxRate(d):
    if d.year <= 2014:
        return 0.09
    return 0.13

def dateStr(d):
    if d is None:
        return ""
    return d.strftime(settings.displayDateLayout)

def _findPayment(items, account):
    for item in items:
        if item.Account == account:
            return item.Date, item.Sum
    return None, 0.0

def dividendHandler():
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', type=str)
    parser.add_argument('--year', type=int, default=datetime.date.today().year)
    args = parser.parse_args()

    securityInfo = security.loadSecurityInfo(settings.securityInfoPath)
    myTrades = loadMyTrades(settings.myTradesPath)
    myDividends = security.loadMyDividends(settings.myDividendsPath)
    buildDividendReport(securityInfo, myTrades, myDividends, args.account, args.year)

if __name__ == "__main__":
    dividendHandler()
