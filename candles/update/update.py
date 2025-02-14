import datetime
import logging
from collections.abc import Callable

import candles

def updateGroup(
    candleInterval: candles.CandleInterval,
    candleProviders,
    candleStorage: candles.CandleStorage,
    startDate: Callable[[str], datetime.datetime],
    checkCandles: Callable[[str, candles.Candle, candles.Candle], None],
    securityCodes: list[str],
):
    "Обновляет котировки"

    if not candleProviders:
        raise ValueError("providers empty")
    
    if not securityCodes:
        raise ValueError("securityCodes empty")
    
    logging.info(f"updateGroup size {len(securityCodes)}")
    
    raise NotImplementedError()
