import os

displayDateLayout = "%d.%m.%Y"

benchmarkSecCode = "MCFTR" #Индекс МосБиржи полной доходности брутто
"Бенчмарк для акций"

candlesPath = os.path.expanduser("~/TradingData")
securityInfoPath = os.path.expanduser("~/Data/assets/StockSettings.xml")
myDividendsPath = os.path.expanduser("~/Data/assets/Dividends.xml")
myTradesPath = os.path.expanduser("~/Data/assets/trades.csv")
