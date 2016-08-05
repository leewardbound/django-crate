import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

class ModelMetaOptionRouter(object):
    """Allows each model to set its own destiny"""
    def db_for_read(self, model, **hints):
        return getattr(model._meta, 'in_db', None)

    def db_for_write(self, model, **hints):
        return getattr(model._meta, 'in_db', None)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        from django.apps import apps
        if not model_name:
            return True
        model = apps.get_model(app_label, model_name)
        # Specify target database with field in_db in model's Meta class
        if hasattr(model._meta, 'in_db'):
            if model._meta.in_db == db:
                return True
            else:
                return False
        else:
            # Random models that don't specify a database can only go to 'default'
            if db == 'default' or model_name == 'Migrations':
                return True
            else:
                return False
