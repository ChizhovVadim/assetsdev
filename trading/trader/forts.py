from .domaintypes import SecurityInfo

FUTURESCLASSCODE = "SPBFUT"

def encodeSecurity(securityCode: str)->str:
	"""
	Sample: "Si-3.17" -> "SiH7"
	http://moex.com/s205
	"""

	#TODO вечные фьючерсы
	#if strings.HasSuffix(securityName, "F") {
	#	return securityName, nil
	#}

	monthCodes = "FGHJKMNQUVXZ"

	delim1 = securityCode.index("-")
	delim2 = securityCode.index(".")

	name = securityCode[:delim1]
	month = int(securityCode[delim1+1:delim2])
	year = int(securityCode[delim2+1:])

	# курс китайский юань – российский рубль
	if name == "CNY":
		name = "CR"

	return f"{name}{monthCodes[month-1]}{year%10}"

def getSecurityInfo(securityName: str)->SecurityInfo:
    if securityName.startswith("Si"):
        return SecurityInfo(
            Name=securityName,
            ClassCode=FUTURESCLASSCODE,
            Code=encodeSecurity(securityName),
            PricePrecision= 0,
			PriceStep= 1,
			PriceStepCost= 1,
			Lever= 1,
        )
    if securityName.startswith("CNY"):
        return SecurityInfo(
            Name=securityName,
            ClassCode=FUTURESCLASSCODE,
            Code=encodeSecurity(securityName),
            PricePrecision= 3,
			PriceStep=      0.001,
			PriceStepCost=  1,
			Lever=          1000,
        )
    raise ValueError("security not found", securityName)
