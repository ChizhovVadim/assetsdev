import argparse
import datetime
from dataclasses import dataclass

import candles
from assets.portfolio.holding import getHoldingTickers
from assets import security
from assets import settings

@dataclass
class QuoteEntry:
    security: str
    price: float
    change: float

def buildChangesReport(start: datetime.datetime,
                       finish: datetime.datetime,
                       secCodes: list[str],
                       secInfo: dict[str, security.SecurityInfo],
                       candleStorage: candles.CandleStorage,
                       dividends: list[security.DividendSchedule]):
    "Отчет об изменении котировок за период. Учитывает дивиденды и сплиты."

    list = []
    for ticker in secCodes:
        si = secInfo[ticker]
        title = si.Title
        startCandle = candleStorage.candleBeforeDate(ticker, start)
        finishCandle = candleStorage.candleByDate(ticker, finish)
        if startCandle and finishCandle:
            sr, divs = _caclSplitRatioAndDividends(start, finish, si, dividends)
            change = (finishCandle.ClosePrice+divs)/startCandle.ClosePrice*sr
            list.append(QuoteEntry(title, finishCandle.ClosePrice, change))
    list.sort(key=lambda x:x.change, reverse=True)

    for entry in list:
        print(f"{entry.security:<12} {entry.price:>10} {(entry.change-1)*100:>6,.1f}")
    print()

def _caclSplitRatioAndDividends(
        start: datetime.datetime,
        finish: datetime.datetime,
        secInfo: security.SecurityInfo,
        ds: list[security.DividendSchedule],
):
    corporateActions = []
    corporateActions.extend(split
              for split in secInfo.Splits 
              if start.date() < split.FixDate.date() <= finish.date())
    corporateActions.extend(div
            for div in ds
            if div.SecurityCode == secInfo.SecurityCode
            and start.date() < div.FixDate.date() <= finish.date())
    corporateActions.sort(key=lambda x:x.FixDate)
    
    totalSplitRatio = 1.0
    totalDividends = 0.0
    
    for action in corporateActions:
        if isinstance(action, security.domaintypes.SplitInfo):
            splitRatio = action.NewQuantity/action.OldQuantity
            totalSplitRatio *= splitRatio
            # дивиденд на 1 акцию нужно пересчитывать с учетом сплита акций
            totalDividends /= splitRatio

        if isinstance(action, security.domaintypes.DividendSchedule):
            totalDividends += action.Rate

    return (totalSplitRatio, totalDividends)

def quotesHandler():
    today = datetime.datetime.today()

    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=datetime.datetime.fromisoformat, default=datetime.datetime(today.year, 1, 1))
    parser.add_argument('--finish', type=datetime.datetime.fromisoformat, default=today)
    parser.add_argument('--dividend', action="store_true")
    args = parser.parse_args()

    secCodes = getHoldingTickers()
    secCodes.append(settings.benchmarkSecCode)
    secInfo = security.loadSecurityInfo(settings.securityInfoPath)
    candleStorage = candles.CandleStorage(settings.candlesPath, candles.CandleInterval.DAILY)
    myDividends = security.loadMyDividends(settings.myDividendsPath) if args.dividend else []

    buildChangesReport(args.start, args.finish, secCodes, secInfo, candleStorage, myDividends)

if __name__ == "__main__":
    quotesHandler()
