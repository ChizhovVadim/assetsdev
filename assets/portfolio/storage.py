import datetime
import csv

from .domaintypes import MyTrade

_dateTimeLayout = "%Y-%m-%dT%H:%M:%S"
_dateLayout     = "%Y-%m-%d"

def _parseMyTrade(row)->MyTrade:
        return MyTrade(SecurityCode=row[0],
            DateTime=datetime.datetime.strptime(row[1], _dateTimeLayout),
            ExecutionDate=datetime.datetime.strptime(row[2], _dateLayout),
            Price=float(row[3]),
            Volume=int(row[4]),
            ExchangeComission=float(row[5]),
            BrokerComission=float(row[6]),
            Account=row[7])

def loadMyTrades(path: str)->list[MyTrade]:
    result = []
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        # skip header
        next(reader)
        for row in reader:
            item = _parseMyTrade(row)
            result.append(item)
    return result

def saveMyTrades(path: str, myTrades: list[MyTrade]):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for t in myTrades:
            data = [
                t.SecurityCode,
                t.DateTime.strftime(_dateTimeLayout),
                t.ExecutionDate.strftime(_dateLayout),
                t.Price,
                t.Volume,
                t.ExchangeComission,
                t.BrokerComission,
                t.Account,
            ]
            writer.writerow(data)
