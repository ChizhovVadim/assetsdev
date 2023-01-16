import enum
import datetime
import urllib
import urllib.request
import urllib.parse
import csv
import internal.historycandle.historycandle

FINAM_CHARSET = "cp1251"
FINAM_TRUSTED_USER_AGENT = "Mozilla/5.0"


class Timeframe(enum.IntEnum):
    TICKS = 1
    MINUTES1 = 2
    MINUTES5 = 3
    MINUTES10 = 4
    MINUTES15 = 5
    MINUTES30 = 6
    HOURLY = 7
    DAILY = 8
    WEEKLY = 9
    MONTHLY = 10


def download(securityCode, timeFrame, beginDate, endDate):
    url = buildUrl(securityCode, timeFrame, beginDate, endDate)
    request = urllib.request.Request(
        url, None, {"User-Agent": FINAM_TRUSTED_USER_AGENT}
    )
    response = urllib.request.urlopen(request)
    # print(response.status)
    data = response.read().decode(FINAM_CHARSET).splitlines()
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
    return internal.historycandle.historycandle.HistoryCandle(dt, o, h, l, c, v)


def buildUrl(securityCode, timeFrame, beginDate, endDate):
    params = {}
    params["em"] = securityCode

    params["df"] = beginDate.day
    params["mf"] = beginDate.month - 1
    params["yf"] = beginDate.year

    params["dt"] = endDate.day
    params["mt"] = endDate.month - 1
    params["yt"] = endDate.year

    params["p"] = Timeframe.DAILY.value

    qstr = urllib.parse.urlencode(params)

    url = "https://export.finam.ru/data.txt?d=d&market=14&f=data.txt&e=.txt&cn=data&dtf=1&tmf=1&MSOR=0&sep=1&sep2=1&datf=1&at=1"
    url += "&" + qstr
    return url
