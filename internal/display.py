import datetime

displayDateLayout = "%d.%m.%Y"

def format_date(d: datetime.datetime)->str:
    global displayDateLayout
    return d.strftime(displayDateLayout) if d else ""

def format_zero(val,fmt):
    return format(val, fmt) if val else ""
