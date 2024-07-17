import xml.etree.ElementTree as et
import datetime
import csv

from .domaintypes import SecurityInfo, MyTrade, DividendSchedule, ReceivedDividend

def loadSecurityInfo(path: str)->dict[str,SecurityInfo]:
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

_dateTimeLayout = "%Y-%m-%dT%H:%M:%S"
_dateLayout     = "%Y-%m-%d"

def _parseMyTrade(row)->MyTrade:
        return MyTrade(SecurityCode=row[0],
            DateTime=datetime.datetime.strptime(row[1], _dateTimeLayout),
            ExecutionDate=datetime.datetime.strptime(row[2], _dateLayout),
            Price=float(row[3]),
            Volume=int(row[4]),
            ExchangeComission=float(row[5]),
            BrokerComission=float(row[6]),
            Account=row[7])

def loadMyTrades(path: str)->list[MyTrade]:
    result = []
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        # skip header
        next(reader)
        for row in reader:
            item = _parseMyTrade(row)
            result.append(item)
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
            RecordDate=datetime.datetime.strptime(recordDate, dateLayout),
            Rate=float(child.attrib["Rate"]),
            Received=received,
        )
        result.append(item)
    return result
