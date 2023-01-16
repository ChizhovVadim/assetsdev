import internal.historycandle.finam as finam

class HistoryCandleProvider:
    def __init__(self, securityInfo):
         self.securityInfo = securityInfo

    def load(self, securityCode, beginDate, endDate):
        if securityCode not in self.securityInfo:
            raise ValueError("securityCode nod found")

        secInfo = self.securityInfo[securityCode]
        if secInfo.FinamCode != "":
            return finam.download(secInfo.FinamCode, finam.Timeframe.DAILY, beginDate, endDate)

        return None
