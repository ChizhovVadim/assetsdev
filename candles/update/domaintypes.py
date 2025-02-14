from typing import NamedTuple

class SecurityInfo(NamedTuple):
    SecurityCode: str
    FinamCode: str
    MfdCode: str

class UpdateError(Exception):
    pass
