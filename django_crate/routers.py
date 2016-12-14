import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

class ModelMetaOptionRouter(object):
    """Allows each model to set its own destiny"""

    def db_for_read(self, model, **hints):
        return getattr(model._meta, 'in_db', None)

    def db_for_write(self, model, **hints):
        return getattr(model._meta, 'in_db', None)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if not model_name:
            # no model, no migration!
            return False
        try:
            from django.apps import apps
            model = apps.get_model(app_label, model_name)
        except LookupError:
            # hm. model does not exist?
            return False
        if hasattr(model._meta, 'in_db'):
            # allow if in_db matches database
            return model._meta.in_db == db
        # otherwise allow if 'default' database
        return db == 'default'
