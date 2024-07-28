import datetime
import logging
import time
import itertools
from collections.abc import Callable

from .storage import CandleStorage
from .domaintypes import Candle

_logger = logging.getLogger("candles.update")
_logger.setLevel(logging.INFO)

def updateGroup(
    candleProviders,
    candleStorage: CandleStorage,
    startDate: Callable[[str], datetime.datetime],
    checkCandles: Callable[[str, Candle, Candle], None],
    securityCodes: list[str],
):
    if not candleProviders:
        raise ValueError("providers empty")
    _logger.info(f"updateGroup {len(securityCodes)} items")
    secCodesFailed = []
    for secCode in securityCodes:
        try:
            updateSignle(candleProviders, candleStorage, startDate, checkCandles, secCode)
        except ValueError:
            secCodesFailed.append(secCode)
        time.sleep(1)
    if len(secCodesFailed) != 0:
        _logger.warning(f"update failed {len(secCodesFailed)} {secCodesFailed}")

def updateSignle(
    candleProviders,
    candleStorage: CandleStorage,
    startDate: Callable[[str], datetime.datetime],
    checkCandles: Callable[[str, Candle, Candle], None],
    securityCode: str,
):
    try:
        lastCandle = candleStorage.last(securityCode)
    except OSError as e:
        _logger.warning(f"no existing data {securityCode} {e}")
        lastCandle = None

    if lastCandle is None:
        beginDate = startDate(securityCode)
    else:
        beginDate = lastCandle.DateTime

    today = datetime.datetime.now()
    endDate = today

    if beginDate>endDate:
        raise ValueError("beginDate>endDate", securityCode, beginDate, endDate)
    
    candles = _downloadCandles(candleProviders, securityCode, beginDate, endDate)
    
    #Последний бар за сегодня может быть еще не завершен
    if candles[-1].DateTime.date() == today.date():
        candles.pop()

    if lastCandle is not None:
        candles = list(itertools.dropwhile(lambda x: x.DateTime <= lastCandle.DateTime, candles))

    if not candles:
        _logger.info(f"no new candles {securityCode}")
        return

    if lastCandle is not None and \
        checkCandles is not None:
        checkCandles(securityCode, lastCandle, candles[0])

    _logger.info(f"downloaded {securityCode} {len(candles)} {candles[0]} {candles[-1]}")
    candleStorage.update(securityCode, candles)

def _downloadCandles(candleProviders,
                     securityCode: str,
                     beginDate: datetime.datetime,
                     endDate: datetime.datetime)->list[Candle]:
    for candleProvider in candleProviders:
        try:
            candles = candleProvider(securityCode, beginDate, endDate)
            if not candles:
                raise ValueError("download empty", securityCode, beginDate, endDate)
        except Exception as e:
            _logger.warning(f"update failed {securityCode} {e}")
        else:
            return candles
        
    raise ValueError("download failed", securityCode, beginDate, endDate)
