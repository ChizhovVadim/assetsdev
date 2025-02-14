
from .domaintypes import SecurityInfo
from .finam import FinamProvider
from .mfd import MfdProvider

# Можно на вход candleInterval, чтобы аналогично candleStorage
def newCandleProvider(key: str, secCodes: dict[str,SecurityInfo]):
    if key == "finam":
        finamCodes = { key: val.FinamCode for key, val in secCodes.items() }
        return FinamProvider(finamCodes)
    if key == "mfd":
        mfdCodes = { key: val.MfdCode for key, val in secCodes.items() }
        return MfdProvider(mfdCodes)
    raise ValueError(f"bad provider {key}")
