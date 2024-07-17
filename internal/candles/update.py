import datetime
import logging
import time
import itertools
import math

from .storage import CandleStorage
from .domaintypes import Candle

class CandleUpdateService:
    def __init__(self, provider, storage: CandleStorage):
         self._provider = provider
         self._storage = storage

    # TODO вначале качаем все с 1 провайдера, а потом failed со второго?
    def updateGroup(self, securityCodes: list[str]):
        logging.info(f"updateGroup {len(securityCodes)} items")
        secCodesFailed = []
        for secCode in securityCodes:
            try:
                self.update(secCode)
            except Exception as e:
                logging.warning(f"update failed {secCode} {e}")
                secCodesFailed.append(secCode)
            time.sleep(1)
        if len(secCodesFailed) != 0:
            logging.warning(f"update failed {len(secCodesFailed)} {secCodesFailed}")

    def update(self, securityCode: str):
        try:
            lastCandle = self._storage.last(securityCode)
        except OSError as e:
            logging.warning(f"no existing data {securityCode} {e}")
            lastCandle = None

        if lastCandle is None:
            #TODO для фьючерсов: expDate-4*month.
            beginDate = datetime.datetime(year=2013, month=1, day=1)
        else:
            beginDate = lastCandle.DateTime

        today = datetime.datetime.now()
        endDate = today

        if beginDate>endDate:
            raise ValueError("beginDate>endDate", securityCode, beginDate, endDate)
        
        candles: list[Candle] = self._provider.load(securityCode, beginDate, endDate)
        if not candles:
            raise ValueError("download empty", securityCode, beginDate, endDate)
        
        #Последний бар за сегодня может быть еще не завершен
        if candles[-1].DateTime.date() == today.date():
            candles.pop()

        candles = list(itertools.dropwhile(lambda x: x.DateTime <= lastCandle.DateTime, candles))

        if not candles:
            logging.info(f"no new candles {securityCode}")
            return

        if lastCandle is not None:
            closeChange = abs(math.log(candles[0].C/lastCandle.C))
            openChange = abs(math.log(candles[0].O/lastCandle.C))
            width = 0.25
            if openChange >= width and closeChange >= width:
                raise ValueError("big jump", securityCode, lastCandle, candles[0])

        logging.info(f"downloaded {securityCode} {len(candles)} {candles[0]} {candles[-1]}")
        self._storage.update(securityCode, candles)
