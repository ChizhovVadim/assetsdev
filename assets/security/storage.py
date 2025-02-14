import xml.etree.ElementTree as et
import datetime

from .domaintypes import SecurityInfo, DividendSchedule, ReceivedDividend, SplitInfo

def loadSecurityInfo(path: str)->dict[str,SecurityInfo]:
    dateLayout = "%Y-%m-%d"
    tree = et.ElementTree(file=path)
    root = tree.getroot()
    result = {}
    for child in root:
        splits = []
        for xe in child.findall("SplitInfo"):
            splits.append(SplitInfo(
                datetime.datetime.strptime(xe.attrib["Date"], dateLayout),
                int(xe.attrib["OldQuantity"]),
                int(xe.attrib["NewQuantity"]),
            ))
        entry = SecurityInfo(
            SecurityCode=child.attrib["Name"],
            Title=child.attrib["Title"],
            Number=child.attrib.get("Number"),
            FinamCode=child.attrib.get("FinamCode"),
            MfdCode=child.attrib.get("MfdCode"),
            Splits=splits,
        )
        result[entry.SecurityCode]=entry
    return result

def loadMyDividends(path: str)->list[DividendSchedule]:
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
            FixDate=datetime.datetime.strptime(recordDate, dateLayout),
            Rate=float(child.attrib["Rate"]),
            Received=received,
        )
        result.append(item)
    return result
