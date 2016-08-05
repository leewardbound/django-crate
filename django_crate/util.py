import datetime, pytz
from django.utils import timezone
def milliseconds(dt=None):
    dt = dt or datetime.datetime.utcnow()
    epoch = datetime.datetime.utcfromtimestamp(0)
    if(dt.tzinfo):
        epoch = epoch.replace(tzinfo=pytz.utc)
    return int((dt - epoch).total_seconds() * 1000)

def allow_model_meta(name):
    import django.db.models.options as options
    if not name in options.DEFAULT_NAMES:
        options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('name',)

def refresh_model(model):
    from django.db import connections
    cursor = connections[getattr(model._meta, 'in_db', 'default')].cursor()
    cursor.execute("refresh table \"%s\"" % model._meta.db_table)
