import xml.etree.ElementTree as et
from . import domaintypes

def loadSettings(path: str)-> domaintypes.TraderSettings:
    tree = et.ElementTree(file=path)
    root = tree.getroot()

    strategyConfigs = []
    for xeStrategyConfig in root.find("StrategyConfigs").findall("StrategyConfig"):
        sPos = xeStrategyConfig.attrib.get("Position")
        strategyConfigs.append(domaintypes.StrategyConfig(
            Name=xeStrategyConfig.attrib["Name"],
            SecurityCode=xeStrategyConfig.attrib["SecurityCode"],
            Lever=float(xeStrategyConfig.attrib.get("Lever")),
            MaxLever=float(xeStrategyConfig.attrib.get("MaxLever")),
            Weight=float(xeStrategyConfig.attrib.get("Weight")),
            StdVolatility=float(xeStrategyConfig.attrib["StdVolatility"]),
            Direction=int(xeStrategyConfig.attrib.get("Direction")),
            Position= float(sPos) if sPos else None,
        ))

    clients = []
    for xeClient in root.find("Clients").findall("Client"):
        sAmount = xeClient.attrib.get("Amount")
        sMaxAmount = xeClient.attrib.get("MaxAmount")
        sWeight = xeClient.attrib.get("Weight")
        clients.append(domaintypes.Client(
            Key=xeClient.attrib["Key"],
            Firm=xeClient.attrib["Firm"],
            Portfolio=xeClient.attrib["Portfolio"],
            Port=int(xeClient.attrib["Port"]),
            Amount= float(sAmount) if sAmount else None,
            MaxAmount=float(sMaxAmount) if sMaxAmount else None,
            Weight=float(sWeight) if sWeight else None,
        ))

    return domaintypes.TraderSettings(clients, strategyConfigs)
