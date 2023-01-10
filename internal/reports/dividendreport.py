from dataclasses import dataclass
import datetime

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

def buildDividendReport(securityInfo, myTrades, myDividends, year):
    if year is None:
        year = datetime.datetime.today().year
    
    items = []
    totalExpected = 0.0
    totalPayment = 0.0
    for d in myDividends:
        if d.RecordDate.year != year: continue

        shares = _calculateShares(myTrades, d.RecordDate, d.SecurityCode)

        title = securityInfo.get(d.SecurityCode).Title
        
        for account, volume in shares.items():
            if volume==0: continue
            expected = _calculateExpectedDividend(d.Rate, volume, d.RecordDate)
            paymentDate, payment = _findPayment(d.Received, account)
            items.append(DividendItem(title, d.RecordDate, d.Rate, account, volume, expected, paymentDate, payment))

            totalExpected += expected
            totalPayment += payment

    items.sort(key=lambda x : x.RecordDate)
    toReceive=max(0, totalExpected-totalPayment)

    print(f"Отчет по дивидендам за '{year}' год")
    print(f"Ожидается {totalExpected:,.0f}")
    print(f"Получено {totalPayment:,.0f}")
    print(f"К получению {toReceive:,.0f}")
    for item in items:
        print(f"{item.Title:<12} {dateStr(item.RecordDate)} {item.Rate:>10,} {item.Account:<6} {item.Shares:>10} {item.Expected:>10,} {dateStr(item.PaymentDate)} {item.Payment:>10,}")

def _calculateShares(myTrades, date, securityCode):
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
    return d.strftime("%Y-%m-%d")

def _findPayment(items, account):
    for item in items:
        if item.Account == account:
            return item.Date, item.Sum
    return None, 0.0
