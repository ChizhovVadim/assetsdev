from dataclasses import dataclass
import datetime
import csv
import os

@dataclass(frozen=True)
class Candle:
    DateTime: datetime.datetime
    O: float
    H: float
    L: float
    C: float
    V: float

class HistoryCandleStorage:
    def __init__(self, historyCandlesFolder):
         self.historyCandlesFolder = historyCandlesFolder

    def fileName(self, securityCode):
        return os.path.join(self.historyCandlesFolder, securityCode+".txt")

    def parseCandle(self, row):
        dt = datetime.datetime.strptime(row[2], "%Y%m%d")
        t = int(row[3])

        hour = t // 10000
        min = (t // 100) % 100
        dt = dt + datetime.timedelta(hours=hour, minutes=min)

        o=float(row[4])
        h=float(row[5])
        l=float(row[6])
        c=float(row[7])
        v=float(row[8])
        return Candle(dt,o,h,l,c,v)

    def read(self, securityCode):
        with open(self.fileName(securityCode), 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',)
            # skip header
            next(reader)
            for row in reader:
                yield self.parseCandle(row)

    def last(self, securityCode):
        result = None
        for candle in self.read(securityCode):
            result = candle
        return result

    def candleByDate(self, securityCode, date):
        result = None
        for candle in self.read(securityCode):
            if candle.DateTime > date:
                break
            result = candle
        return result

    def candleBeforeDate(self, securityCode, date):
        result = None
        for candle in self.read(securityCode):
            if candle.DateTime >= date:
                break
            result = candle
        return result
