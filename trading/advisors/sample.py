from candles import Candle
from .domaintypes import Advice

def testAdvisor(name: str):
    advisor = _makeAdvisor(name)
    return advisor

def _makeAdvisor(name: str):
    if name == "buyandhold":
        return _buyAndHoldAdvisor
    raise ValueError(f"bad advisor {name}")

def _buyAndHoldAdvisor(c: Candle)-> Advice:
    return Advice(c.SecurityCode, c.DateTime, c.ClosePrice, 1.0, "buyAndHold")
