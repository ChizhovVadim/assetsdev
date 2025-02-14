import xml.etree.ElementTree as et
from .domaintypes import SecurityInfo

def loadSecurityCodes(path: str)->dict[str,SecurityInfo]:
    tree = et.ElementTree(file=path)
    root = tree.getroot()
    result = {}
    for child in root:        
        entry = SecurityInfo(
            SecurityCode=child.attrib["Name"],
            FinamCode=child.attrib.get("FinamCode"),
            MfdCode=child.attrib.get("MfdCode"),
        )
        result[entry.SecurityCode]=entry
    return result

def loadFortsCodes(path: str)->dict[str,SecurityInfo]:
    tree = et.ElementTree(file=path)
    root = tree.getroot()
    result = {}
    for child in root.find("SecurityCodes"):
        entry = SecurityInfo(
            SecurityCode=child.attrib["Code"],
            FinamCode=child.attrib.get("FinamCode"),
            MfdCode=child.attrib.get("MfdCode"),
        )
        result[entry.SecurityCode]=entry
    return result
