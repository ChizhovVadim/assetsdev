import internal.dal.candlestorage
import internal.dal.mytradestorage
import internal.dal.securityinfostorage
import internal.dal.dividendstorage
import internal.reports.balancereport
import internal.reports.dividendreport
import internal.reports.pnlreport
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

def main():
     candleStorage = internal.dal.candlestorage.HistoryCandleStorage("/Users/vadimchizhov/TradingData/Portfolio")
     securityInfo = internal.dal.securityinfostorage.loadSecurityInfo("/Users/vadimchizhov/Data/assets/StockSettings.xml")
     myTrades = internal.dal.mytradestorage.loadMyTrades("/Users/vadimchizhov/Data/assets/trades.csv")
     myDividends = internal.dal.dividendstorage.loadMyDividends("/Users/vadimchizhov/Data/assets/Dividends.xml")

     cmdName = cli.commandName()
     if cmdName == "balance":
          balanceHandler(myTrades, candleStorage, securityInfo)
     elif cmdName == "dividend":
          dividendHandler(securityInfo, myTrades, myDividends)
     elif cmdName == "pnl":
          pnlHandler(securityInfo, myTrades, myDividends, candleStorage)
     else:
          print("command not found", cmdName)

if __name__ == "__main__":
    main()
