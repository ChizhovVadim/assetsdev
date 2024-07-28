import sys
import os
import csv
import datetime
import time
import argparse
from . import domaintypes, storage

def importHandler(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', type=str, required=True)
    args = parser.parse_args(argv)

    path = os.path.expanduser("~/src.txt")
    myTrades=loadMyTradesSberbank(path, args.account)
    storage.saveMyTrades(os.path.expanduser("~/dst.txt"), myTrades)

def _parseMoney(s: str)-> float:
    return float(s.replace(" ", ""))

# Копируем сделки из html отчета в блокнот без форматирования
def loadMyTradesSberbank(path: str, account: str)->list[domaintypes.MyTrade]:
    parseDateLayout = "%d.%m.%Y"
    parseTimeLayout = "%H:%M:%S"
    result = []
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            volume = int(row[7])
            if row[6]=="Покупка":
                pass
            elif row[6]=="Продажа":
                volume*=-1
            else:
                raise ValueError("trade direction failed",row[6])
            tradeDate = datetime.datetime.strptime(row[0], parseDateLayout)
            tradeTime = time.strptime(row[2], parseTimeLayout)
            tradeDate = tradeDate.replace(hour=tradeTime.tm_hour,
                              minute=tradeTime.tm_min,
                              second=tradeTime.tm_sec)
            result.append(domaintypes.MyTrade(
                SecurityCode=row[4],
                DateTime=tradeDate,
                ExecutionDate=datetime.datetime.strptime(row[1], parseDateLayout),
                Price=_parseMoney(row[8]),
                Volume=volume,
                BrokerComission=_parseMoney(row[11]),
                ExchangeComission=_parseMoney(row[12]),
                Account=account,
            ))
    return result

if __name__ == "__main__":
    importHandler(sys.argv[1:])
