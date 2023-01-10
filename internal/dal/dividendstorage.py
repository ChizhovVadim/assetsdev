import xml.etree.ElementTree as et
from dataclasses import dataclass
import datetime

@dataclass(frozen=True)
class ReceivedDividend:
    Account: str
    Date: datetime.date
    Sum: float

@dataclass(frozen=True)
class DividendSchedule:
    SecurityCode: str
    RecordDate: datetime.datetime
    Rate: float
    Received: list[ReceivedDividend]

def loadMyDividends(path):
    dateLayout = "%Y-%m-%d"
    result = []
    tree = et.ElementTree(file=path)
    root = tree.getroot()
    for child in root:
        recordDate = child.attrib.get("RecordDate")
        if recordDate is None: continue

        received=[]
        if "RecieveDate" in child.attrib:
            entry=ReceivedDividend(
                Account=child.attrib["Account"],
                Date=datetime.datetime.strptime(child.attrib["RecieveDate"], dateLayout),
                Sum=float(child.attrib["RecieveSum"]),
            )
            received.append(entry)

        for xmlReceived in child:
            entry=ReceivedDividend(
                Account=xmlReceived.attrib["Account"],
                Date=datetime.datetime.strptime(xmlReceived.attrib["Date"], dateLayout),
                Sum=float(xmlReceived.attrib["Sum"]),
            )
            received.append(entry)

        item = DividendSchedule(
            SecurityCode=child.attrib["Name"],
            RecordDate=datetime.datetime.strptime(recordDate, dateLayout),
            Rate=float(child.attrib["Rate"]),
            Received=received,
        )
        result.append(item)
    return result
