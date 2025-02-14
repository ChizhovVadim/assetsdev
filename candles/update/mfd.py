import datetime
import urllib
import urllib.request
import urllib.parse
import csv
import logging

from candles.domaintypes import Candle, CandleInterval
from .domaintypes import UpdateError

class MfdProvider:
    def __init__(self, secCodes: dict[str,str]):
         self._secCodes = secCodes

    def name(self)-> str:
         return "mfd"
    
    def load(self, secCode: str, candleInterval: CandleInterval,
             beginDate: datetime.datetime, endDate: datetime.datetime)-> list[Candle]:
          
          tfCode = _timeFrameCode(candleInterval)
          if tfCode is None:
               raise UpdateError("timeframe code nod found", candleInterval)
          
          mfdCode = self._secCodes.get(secCode)
          if not mfdCode:
               raise UpdateError("security code nod found", secCode)
          
          url = _buildUrl(mfdCode, tfCode, beginDate, endDate)
          logging.debug(f"download from {url}")
          return _download(url, secCode)


def _download(url: str, securityName: str)-> list[Candle]:
    CHARSET = "cp1251"
    TRUSTED_USER_AGENT = "Mozilla/5.0"

    request = urllib.request.Request(
        url, None, {"User-Agent": TRUSTED_USER_AGENT}
    )
    response = urllib.request.urlopen(request, timeout=30)
    # print(response.status)
    data = response.read().decode(CHARSET).splitlines()
    cr = csv.reader(data)
    next(cr)  # skip header
    result = []
    for row in cr:
        item = _parseCandle(row, securityName)
        result.append(item)
    return result

def _parseCandle(row, securityName: str):
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
    return Candle(securityName, dt, o, h, l, c, v)

def _buildUrl(securityCode: str, timeFrameCode: int,
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

def _timeFrameCode(tf: CandleInterval)->int:
    if tf == CandleInterval.MINUTES5:
        return 2
    elif tf == CandleInterval.HOURLY:
        return 6
    elif tf == CandleInterval.DAILY:
        return 7
    else:
        return None
