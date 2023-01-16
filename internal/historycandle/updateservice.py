import datetime
import logging
import time

class CandleUpdateService:
    def __init__(self, historyCandleStorage, historyCandleProvider):
         self.historyCandleStorage = historyCandleStorage
         self.historyCandleProvider = historyCandleProvider

    def update(self, securityCodes):
        secCodesFailed = []

        for secCode in securityCodes:
            try:
                self.updateSingle(secCode)
            except Exception as error:
                logging.warn(f"CandleUpdateService.update fail {secCode} {error}")
                secCodesFailed.append(secCode)
            time.sleep(1.0)

        if len(secCodesFailed)>0:
            raise ValueError("CandleUpdateService.Update failed for", secCodesFailed)

    def updateSingle(self, securityCode):
        lastCandle = self.historyCandleStorage.last(securityCode)

        today = datetime.datetime.today()

        beginDate = lastCandle.DateTime
        endDate = today
        if beginDate>endDate:
            raise ValueError("beginDate>endDate", securityCode)
        
        logging.info(f"dowloading {securityCode} {beginDate:%Y-%m-%d} {endDate:%Y-%m-%d}")
        candles = self.historyCandleProvider.load(securityCode, beginDate, endDate)
        logging.info(f"dowloaded candles {candles[0]}-{candles[-1]}")
