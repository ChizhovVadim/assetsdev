from candles import Candle
from .domaintypes import Advice

def testAdvisor(name: str):
    if name == "buyandhold":
        return buyAndHoldAdvisor
    if name == "openweek":
        return openWeekAdvisor()
    raise ValueError(f"bad advisor {name}")

def buyAndHoldAdvisor(c: Candle)-> Advice:
    return Advice(c.SecurityCode, c.DateTime, c.C, 1.0, "buyAndHold")

def openWeekAdvisor():
    # TODO 2 раза в день в фиксированное время смотрим цена выше/ниже цены открытия недели.
    # Выше - long, ниже - short.
    ratio = 0.0
    def advisor(c: Candle)->Advice:
        return Advice(c.SecurityCode, c.DateTime, c.C, ratio, "openWeek")
    return advisor
