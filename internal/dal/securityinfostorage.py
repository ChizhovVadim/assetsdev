import xml.etree.ElementTree as et
from dataclasses import dataclass

@dataclass(frozen=True)
class SecurityInfo:
    SecurityCode: str
    Title: str
    Number: str
    FinamCode: str
    MfdCode: str

def loadSecurityInfo(path):
    tree = et.ElementTree(file=path)
    root = tree.getroot()
    result = {}
    for child in root:
        entry = SecurityInfo(
            SecurityCode=child.attrib["Name"],
            Title=child.attrib["Title"],
            Number=child.attrib.get("Number", ""),
            FinamCode=child.attrib.get("FinamCode", ""),
            MfdCode=child.attrib.get("MfdCode", ""),
        )
        result[entry.SecurityCode]=entry
    return result
