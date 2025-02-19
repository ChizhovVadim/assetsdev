import os
import candles

displayDateLayout = "%d.%m.%Y"
candlesPath = os.path.expanduser("~/TradingData")
defaultCandleInterval = candles.CandleInterval.MINUTES5
fortsSecurityCodesPath = os.path.expanduser("~/Projects/advisordev/advisor.xml")
traderSettingsPath = os.path.expanduser("~/TradingData/luatrader.xml")
