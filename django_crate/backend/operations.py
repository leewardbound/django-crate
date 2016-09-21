# -*- coding: utf-8 -*-
from django.db.backends.base.operations import BaseDatabaseOperations
from django_crate.util import milliseconds
from django.conf import settings
from django.utils import timezone, six
from datetime import datetime
from dateutil import parser
import pytz

class DatabaseOperations(BaseDatabaseOperations):

    compiler_module = "django_crate.backend.compiler"

    def cache_key_culling_sql(self):
        """not implemented"""
        return None

    def distinct_sql(self, fields):
        if fields:
            return 'DISTINCT {0}'.format(', '.join(fields))
        else:
            return ''

    def date_trunc_sql(self, lookup_type, field_name):
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    datetime_trunc_sql = date_trunc_sql

    def datetime_cast_sql(self):
        """TODO: ?"""
        return super(DatabaseOperations, self).datetime_cast_sql()

    def drop_foreignkey_sql(self):
        """not supported"""
        return ''

    def drop_sequence_sql(self, table):
        """not supported"""
        return ''

    def for_update_sql(self, nowait=False):
        return ''

    def fulltext_search_sql(self, field_name):
        """TODO: support new extended match predicate"""
        return 'match(%s, %%s)' % field_name

    def no_limit_value(self):
        return None

    def regex_lookup(self, lookup_type):
        return '%%s ~ %%s'

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return '"%s"' % name

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        return [
            'DELETE FROM {0}'.format(table) for table in tables
        ]

    def adapt_datetimefield_value(self, value):
        if not value: return None
        if timezone.is_aware(value):
            if settings.USE_TZ:
                value = timezone.make_naive(value, self.connection.timezone)
        value = milliseconds(value)
        return six.text_type(value)

    def value_to_db_date(self, value):
        """transform a date or time value to milliseconds since epoque"""
        if isinstance(value, (datetime, time, date)):
            if(hasattr(value, 'timestamp')):
                return int(value.timestamp() * 1000)
            else:
                return milliseconds(value)
        return value

    value_to_db_datetime = value_to_db_time = value_to_db_date

    def start_transaction_sql(self):
        """not supported"""
        return ''

    def end_transaction_sql(self, success=True):
        """not supported"""
        return ''

    def get_db_converters(self, expression):
        converters = super(DatabaseOperations, self).get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()
        #if internal_type == 'TextField':
        #    converters.append(self.convert_textfield_value)
        #elif internal_type in ['BooleanField', 'NullBooleanField']:
        #    converters.append(self.convert_booleanfield_value)
        if internal_type == 'DateTimeField':
            converters.append(self.convert_datetimefield_value)
        #elif internal_type == 'UUIDField':
        #    converters.append(self.convert_uuidfield_value)
        return converters

    def convert_datetimefield_value(self, value, expression, connection, context):
        if value:
            if(isinstance(value, six.string_types)):
                try:
                    value = int(value)
                except:
                    value = parser.parse(value)
            if(isinstance(value, int)):
                value = datetime.utcfromtimestamp(value / 1e3)
            if not settings.USE_TZ:
                value = value.replace(tzinfo=None)
            else:
                value = self.connection.timezone.localize(value)
        return value
