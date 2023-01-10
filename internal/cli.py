import sys
import datetime

def _parseCommandLine():
    cmdName = ""
    flags = {}
    args = sys.argv
    for i in range(1, len(args)):
        arg = args[i]
        if arg.startswith("-"):
            if i < len(args)-1:
                k = arg.strip("-")
                v = args[i+1]
            flags[k]=v
        elif cmdName=="":
            cmdName = arg

    return cmdName, flags

_cmdName, _cmdParams = _parseCommandLine()

def commandName():
    return _cmdName

def readString(name):
    if name in _cmdParams:
          return _cmdParams[name]
    else:
          return ""

def readDate(name):
    if name in _cmdParams:
         return datetime.datetime.strptime(_cmdParams[name], "%Y-%m-%d")
    else:
         return None

def readInt(name):
    if name in _cmdParams:
         return int(_cmdParams[name])
    else:
         return None
