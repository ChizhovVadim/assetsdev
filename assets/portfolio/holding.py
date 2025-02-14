
from assets import settings
from .storage import loadMyTrades

# TODO возвращать set?
def getHoldingTickers()->list[str]:
    """Список акций, которые есть в портфеле.
    По умолчанию по ним можно обновлять котировки и следить за изменением цен.
    """

    myTrades = loadMyTrades(settings.myTradesPath)
    d = {}
    for t in myTrades:
        d[t.SecurityCode] = d.get(t.SecurityCode, 0) + t.Volume
    return [k for k, v in d.items() if v != 0]
