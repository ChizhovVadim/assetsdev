import os
import logging
import internal.dal.candlestorage
import internal.dal.mytradestorage
import internal.dal.securityinfostorage
import internal.dal.dividendstorage
import internal.reports.balancereport
import internal.reports.dividendreport
import internal.reports.pnlreport
import internal.historycandle.updateservice
import internal.historycandle.provider
import internal.cli as cli

def balanceHandler(myTrades, candleStorage, securityInfo):
     account = cli.readString("account")
     date = cli.readDate("date")
     internal.reports.balancereport.printReport(internal.reports.balancereport.buildBalanceReport(myTrades, candleStorage, securityInfo, account, date))

def dividendHandler(securityInfo, myTrades, myDividends):
     year = cli.readInt("year")
     internal.reports.dividendreport.buildDividendReport(securityInfo, myTrades, myDividends, year)

def pnlHandler(securityInfo, myTrades, myDividends, candleStorage):
     account = cli.readString("account")
     startDate = cli.readDate("start")
     finishDate = cli.readDate("finish")
     internal.reports.pnlreport.buildPnLReport(securityInfo, myTrades, myDividends, candleStorage, account, startDate, finishDate)

def getTickers(myTrades, holding):
     m = {}
     for t in myTrades:
          m[t.SecurityCode] = m.get(t.SecurityCode, 0) + t.Volume

     result = []
     for k, v in m.items():
          if holding and v == 0: continue
          result.append(k)

     return result

def updateHandler(myTrades, candleUpdateService):
     securityCodes = []
     
     secCode = cli.readString("code")
     if secCode != "":
          securityCodes.append(secCode)
     else:          
          micexIndex = "MICEXINDEXCF"
          USDCbrf = "USDCB"

          securityCodes = getTickers(myTrades, True)
          securityCodes.append(micexIndex)
          securityCodes.append(USDCbrf)

     candleUpdateService.update(securityCodes)

def main():
     logging.basicConfig(level="INFO")

     candleStorage = internal.dal.candlestorage.HistoryCandleStorage(os.path.expanduser("~/TradingData/Portfolio"))
     securityInfo = internal.dal.securityinfostorage.loadSecurityInfo(os.path.expanduser("~/Data/assets/StockSettings.xml"))
     myTrades = internal.dal.mytradestorage.loadMyTrades(os.path.expanduser("~/Data/assets/trades.csv"))
     myDividends = internal.dal.dividendstorage.loadMyDividends(os.path.expanduser("~/Data/assets/Dividends.xml"))
     candleUpdateService = internal.historycandle.updateservice.CandleUpdateService(candleStorage,
          internal.historycandle.provider.HistoryCandleProvider(securityInfo))

     cmdName = cli.commandName()
     if cmdName == "balance":
          balanceHandler(myTrades, candleStorage, securityInfo)
     elif cmdName == "dividend":
          dividendHandler(securityInfo, myTrades, myDividends)
     elif cmdName == "pnl":
          pnlHandler(securityInfo, myTrades, myDividends, candleStorage)
     elif cmdName == "update":
          updateHandler(myTrades, candleUpdateService)
     else:
          print("command not found", cmdName)

if __name__ == "__main__":
    main()
