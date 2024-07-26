import datetime
import urllib
import urllib.request
import urllib.parse
import csv
import logging

from .domaintypes import Candle, Timeframe

def load(securityName: str, 
         beginDate: datetime.datetime,
         endDate: datetime.datetime,
         secCodes: dict[str, str],
         timeFrame: Timeframe) -> list[Candle]:
    
        ProviderName = "Finam"
        
        tfCode = _timeFrameCode(timeFrame)
        if tfCode is None:
            raise ValueError("timeframe code nod found", timeFrame, ProviderName)
        
        secCode = secCodes.get(securityName)
        if not secCode:
            raise ValueError("security code nod found", securityName, ProviderName)
        
        url = _buildUrl(secCode, tfCode, beginDate, endDate)
        logging.debug(f"download {ProviderName} {securityName} from {url}")
        return _downloadCandles(url, securityName)    

def _downloadCandles(url: str, securityName: str)-> list[Candle]:
    FINAM_CHARSET = "cp1251"
    FINAM_TRUSTED_USER_AGENT = "Mozilla/5.0"

    request = urllib.request.Request(
        url, None, {"User-Agent": FINAM_TRUSTED_USER_AGENT}
    )
    response = urllib.request.urlopen(request, timeout=30)
    # print(response.status)
    data = response.read().decode(FINAM_CHARSET).splitlines()
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
    v = float(row[8]) #Объемы торгов у mfd и finam для фьючерсов не совпадают?
    return Candle(dt, o, h, l, c, v)


def _buildUrl(securityCode: str, timeFrameCode: int,
             beginDate: datetime.datetime, endDate: datetime.datetime):
    params = {}
    params["em"] = securityCode

    params["df"] = beginDate.day
    params["mf"] = beginDate.month - 1
    params["yf"] = beginDate.year

    params["dt"] = endDate.day
    params["mt"] = endDate.month - 1
    params["yt"] = endDate.year

    params["p"] = timeFrameCode

    qstr = urllib.parse.urlencode(params)

    url = "https://export.finam.ru/data.txt?d=d&market=14&f=data.txt&e=.txt&cn=data&dtf=1&tmf=1&MSOR=0&sep=1&sep2=1&datf=1&at=1"
    url += "&" + qstr
    return url

def _timeFrameCode(tf: Timeframe)->int:
    if tf == Timeframe.MINUTES5:
        return 3
    elif tf == Timeframe.HOURLY:
        return 7
    elif tf == Timeframe.DAILY:
        return 8
    else:
        return None
