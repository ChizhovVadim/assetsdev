import datetime
import urllib
import urllib.request
import urllib.parse
import csv
import logging

from .domaintypes import Candle, Timeframe

class MfdProvider:
    def __init__(self, secCodes: dict[str, str], timeFrame: Timeframe):
        self._secCodes = secCodes
        tfCode = timeFrameCode(timeFrame)
        if tfCode is None:
            raise ValueError("timeframe code nod found", timeFrame)
        self._tfCode = tfCode

    def load(self, securityName: str,
              beginDate: datetime.datetime, endDate: datetime.datetime) -> list[Candle]:
        
        secCode = self._secCodes.get(securityName)
        if not secCode:
            raise ValueError("security code nod found", securityName)
        
        url = buildUrl(secCode, self._tfCode, beginDate, endDate)
        logging.debug(f"download {securityName} from {url}")
        return download(url)
        

def download(url: str)-> list[Candle]:
    CHARSET = "cp1251"
    TRUSTED_USER_AGENT = "Mozilla/5.0"

    request = urllib.request.Request(
        url, None, {"User-Agent": TRUSTED_USER_AGENT}
    )
    response = urllib.request.urlopen(request)
    # print(response.status)
    data = response.read().decode(CHARSET).splitlines()
    cr = csv.reader(data)
    next(cr)  # skip header
    result = []
    for row in cr:
        item = parseCandle(row)
        result.append(item)
    return result

def parseCandle(row):
    dt = datetime.datetime.strptime(row[2], "%Y%m%d")
    t = int(row[3])

    hour = t // 10000
    min = (t // 100) % 100
    dt = dt + datetime.timedelta(hours=hour, minutes=min)

    o = float(row[4])
    h = float(row[5])
    l = float(row[6])
    c = float(row[7])
    v = float(row[8])
    return Candle(dt, o, h, l, c, v)


def buildUrl(securityCode: str, timeFrameCode: int,
             beginDate: datetime.datetime, endDate: datetime.datetime):
    params = {}

    dateLayout = "%d.%m.%Y" #Можно указывать часы, минуты?
    params["Tickers"] = securityCode
    params["Period"] = timeFrameCode
    params["StartDate"] = beginDate.strftime(dateLayout)
    params["EndDate"] = endDate.strftime(dateLayout)

    qstr = urllib.parse.urlencode(params)

    url = "http://mfd.ru/export/handler.ashx/data.txt?TickerGroup=26&Alias=false&timeframeValue=1&timeframeDatePart=day&SaveFormat=0&SaveMode=0&FileName=data.txt&FieldSeparator=%2C&DecimalSeparator=.&DateFormat=yyyyMMdd&TimeFormat=HHmmss&DateFormatCustom=&TimeFormatCustom=&AddHeader=true&RecordFormat=0&Fill=false"
    url += "&" + qstr
    return url

def timeFrameCode(tf: Timeframe)->int:
    if tf == Timeframe.MINUTES5:
        return 2
    elif tf == Timeframe.HOURLY:
        return 6
    elif tf == Timeframe.DAILY:
        return 7
    else:
        return None
