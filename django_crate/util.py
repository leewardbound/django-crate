import datetime, pytz
from django.utils import timezone
def milliseconds(dt=None):
    dt = dt or datetime.datetime.utcnow()
    epoch = datetime.datetime.utcfromtimestamp(0)
    if(dt.tzinfo):
        epoch = epoch.replace(tzinfo=pytz.utc)
    return int((dt - epoch).total_seconds() * 1000)
