from dataclasses import dataclass
import datetime
import internal.xirr as xirr

@dataclass
class BalanceEntry:
    VolumeStart: int
    VolumeFinish: int

def buildPnLReport(securityInfo, myTrades, myDividends, candleStorage,
    account, startDate, finishDate):
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
        if not(account=="" or t.Account==account): continue
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

    arsageraRate, arsageraAnnualRate = xirr.arsageraRate(payments)

    benchmarkTicker = "MICEXINDEXCF"
    benchmarkRate = candleStorage.candleByDate(benchmarkTicker, finishDate).C/candleStorage.candleByDate(benchmarkTicker, startDate).C
    benchmarkAnnualRate = pow(benchmarkRate, 1.0/xirr.yearsBetween(startDate, finishDate))

    print(f"СЧА на начало периода {amountStart:,.0f}")
    print(f"СЧА на конец периода {amountFinish:,.0f}")
    print(f"Инвестировано новых средств {totalAddition:,.0f}")
    print(f"Дивиденды {totalDividends:,.0f}")
    print(f"Комиссия {totalCommission:,.0f}")
    print(f"Прибыль {PnL:,.0f}")
    print(f"Прибыль {(arsageraRate-1)*100:.1f}%")
    print(f"Прибыль {(arsageraAnnualRate-1)*100:.1f}% годовых")
    print(f"Бенчмарк {(benchmarkRate-1)*100:.1f}%")
    print(f"Бенчмарк {(benchmarkAnnualRate-1)*100:.1f}% годовых")
