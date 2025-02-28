import logging
import math

import candles
from assets import security

def checkPriceChange(securityCode: str,
                     x: candles.Candle,
                     y: candles.Candle,
                     width: float,
                     securityInfo: dict[str, security.SecurityInfo]):
    "Кидает ValueError, если большая разница цен x и y. Учитывает информацию о сплите акций."
        
    closeChange = abs(math.log(x.ClosePrice / y.ClosePrice))
    openChange = abs(math.log(x.ClosePrice / y.OpenPrice))

    if not(openChange >= width and closeChange >= width):
        return
    if securityInfo is None:
        return
    
    splits = securityInfo[securityCode].Splits
    for split in splits:
        if x.DateTime < split.FixDate < y.DateTime:
            logging.info(f"split found {split}")
            return

    raise ValueError("big jump", securityCode, x, y)
