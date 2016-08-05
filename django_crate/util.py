import datetime, pytz
from django.utils import timezone
import time
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
    refresh_sql = "refresh table \"%s\"" % model._meta.db_table
    #cursor = connections[getattr(model._meta, 'in_db', 'default')].cursor()
    #cursor.execute()
    model.objects.raw(refresh_sql)

def wait_until_exists(get_qs, pk, timeout=5, increment=0.1):
    start = time.time()
    while time.time() < (start + timeout):
        qs = get_qs()
        refresh_model(qs.model)
        try:
            if qs.get(pk=pk): return qs
        except qs.model.DoesNotExist: pass
        time.sleep(increment)
    return get_qs()

