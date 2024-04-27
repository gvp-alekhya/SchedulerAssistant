from datetime import datetime
import re

def getDateFromStringISOFormat(datetime_str):
    return datetime.fromisoformat(datetime_str)

def getISOString(dateObject):
    return dateObject.isoformat()
