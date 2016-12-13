# -*- coding: utf-8 -*-

import json
from django.core.exceptions import ImproperlyConfigured
from django.db.backends.base.base import BaseDatabaseWrapper

try:
    import psycopg2 as Database
    import psycopg2.extensions
    import psycopg2.extras
except ImportError as e:
    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor
from .validation import DatabaseValidation


class DatabaseWrapper(BaseDatabaseWrapper):

    vendor = 'crate'
    operators = {
        'exact': '= %s',
        'iexact': '= %s',
        'contains': 'LIKE %s',
        'icontains': 'LIKE %s',
        'regex': '~ %s',
        'iregex': '~ %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'LIKE %s',
        'iendswith': 'LIKE %s',
    }

    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = DatabaseValidation(self)

    def get_connection_params(self):
        settings_dict = self.settings_dict
        if settings_dict['NAME'] == '':
            raise ImproperlyConfigured(
                "settings.DATABASES is improperly configured. "
                "Please supply the NAME value.")
        conn_params = {}
        conn_params.update(settings_dict['OPTIONS'])
        conn_params.pop('isolation_level', None)
        conn_params['database'] = settings_dict['NAME'] or 'doc'
        conn_params['host'] = settings_dict['HOST'] or 'localhost'
        conn_params['port'] = settings_dict['PORT'] or 5432
        return conn_params

    def create_cursor(self):
        return self.connection.cursor()

    def init_connection_state(self):
        self.connection.set_client_encoding('UTF8')

    def get_new_connection(self, conn_params):
        return Database.connect(**conn_params)

    def schema_editor(self, *args, **kwargs):
        return DatabaseSchemaEditor(self, *args, **kwargs)

    ### Unsupported in crate
    def _commit(self):
        pass

    def _savepoint(self, sid):
        pass

    def _savepoint_rollback(self, sid):
        pass

    def _savepoint_commit(self, sid):
        pass

    def _savepoint_allowed(self):
        return False

    def _set_autocommit(self, autocommit):
        pass

    def rollback(self):
        pass

    def check_constraints(self, table_names=None):
        pass

    def is_usable(self):
        try:
            with self.create_cursor() as cur:
                cur.execute("SELECT 1")
        except Database.Error:
            return False
        else:
            return True


def adapt_dict(val):
    as_crate = '{%s}'%', '.join(
            '"%s" = %s'%(str(psycopg2.extensions.adapt(k))[1:-1], psycopg2.extensions.adapt(v))
        for k, v in val.items()
    )
    return psycopg2.extensions.AsIs(as_crate)
psycopg2.extensions.register_adapter(dict, adapt_dict)


def adapt_list(val):
    as_crate = '[%s]'%', '.join(str(psycopg2.extensions.adapt(v)) for v in val)
    return psycopg2.extensions.AsIs(as_crate)
psycopg2.extensions.register_adapter(list, adapt_list)
