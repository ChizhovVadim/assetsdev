import datetime
import argparse
import logging

import candles
from candles.update.seccode import loadFortsCodes
from candles.update.candleprovider import newCandleProvider

from trading import settings

def testDownloadHandler():
    logging.basicConfig(level=logging.DEBUG)
    today = datetime.datetime.today()

    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', type=str, required=True)
    parser.add_argument('--timeframe', type=str, default=settings.defaultCandleInterval)
    parser.add_argument('--security', type=str, required=True)
    parser.add_argument('--start', type=datetime.datetime.fromisoformat, default=today+datetime.timedelta(days=-7))
    parser.add_argument('--finish', type=datetime.datetime.fromisoformat, default=today)
    args = parser.parse_args()
    candleInterval = candles.CandleInterval(args.timeframe)
    
    provider = newCandleProvider(args.provider, loadFortsCodes(settings.fortsSecurityCodesPath))
    downloadedCandles = provider.load(args.security, candleInterval, args.start, args.finish)
    
    if not downloadedCandles:
        print("candles empty")
    elif len(downloadedCandles)<= 10:
        print(f"downloaded size {len(downloadedCandles)} candles {downloadedCandles}")
    else:
        print(f"downloaded size {len(downloadedCandles)} head {downloadedCandles[:5]} tail {downloadedCandles[-5:]}")

if __name__ == "__main__":
    testDownloadHandler()
