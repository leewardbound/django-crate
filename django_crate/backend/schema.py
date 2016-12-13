# -*- coding: utf-8; -*-
import time
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.utils import six
from django.utils.text import force_text
from .creation import DatabaseCreation
TYPES = DatabaseCreation.data_types


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    sql_create_table = "CREATE TABLE %(table)s (%(definition)s) %(partitioned_by)s %(clustered_by)s %(settings)s"
    sql_delete_table = "DROP TABLE %(table)s"
    sql_create_index = None
    sql_delete_index = None

    def column_sql(self, model, field, include_default=False):
        # Get the column's type and use that as the basis of the SQL
        db_params = field.db_parameters(connection=self.connection)
        sql = db_params['type'] or TYPES.get(field.get_internal_type(), None)
        params = []
        # Check for fields that aren't actually columns (e.g. M2M)
        if sql is None:
            # TODO: handle compound indices here?
            return None, None

        # Work out nullability
        null = field.null
        if null and not self.connection.features.implied_column_null:
            # Not supported by CrateDB
            pass
        elif not null:
            sql += " NOT NULL"

        # Primary key/unique outputs
        if field.primary_key:
            sql += " PRIMARY KEY"
        elif field.unique:
            # Not supported by CrateDB
            pass

        fulltext_index = getattr(field, 'fulltext_index', None)
        if fulltext_index:
            if fulltext_index.lower() == 'off':
                sql += " INDEX OFF"
            elif fulltext_index.lower() == "fulltext":
                sql += " INDEX USING {}".format(fulltext_index.upper())
                analyzer = getattr(field, 'analyzer', None)
                if analyzer is not None:
                    sql += " WITH (analyzer=?)"
                    params.append(analyzer)
            elif fulltext_index.lower() == "plain":
                sql += " INDEX USING {}".format(fulltext_index.upper())

        return sql, params

    def skip_default(self, field):
        """
        crate does not support default values yet
        """
        return True

    def quote_value(self, value):
        if isinstance(value, six.string_types):
            return "'%s'" % self.escape_string(value)
        if isinstance(value, six.buffer_types):
            return "'%s'" % self.escape_string(force_text(value))
        return str(value)

    def escape_string(self, value):
        """
        escape single ' inside a string with ''
        """
        return value.replace("'", "''")

    def create_model(self, model):
        column_sqls = []
        params = []

        for field in model._meta.local_fields:
            # SQL
            definition, extra_params = self.column_sql(model, field)
            if definition is None:
                continue

            # Add the SQL to our big list
            column_sqls.append("%s %s" % (
                self.quote_name(field.column),
                definition,
            ))

        # Make the table
        sql = self.sql_create_table % {
            "table": self.quote_name(model._meta.db_table),
            "definition": ", ".join(column_sqls),
            "clustered_by": self._clustered_by_sql(model, params),
            "partitioned_by": self._partitioned_by_sql(model, params),
            "settings": self._table_settings_sql(model, params),
        }

        # Prevent using [] as params, in the case a literal '%' is used in the definition
        self.execute(sql, params or None)
        # wait for shards to start
        # let's do this optimistically ...
        time.sleep(2)

    def _clustered_by_sql(self, model, params):
        clustered_by = getattr(model._meta, "clustered_by", None)
        number_of_shards = getattr(model._meta, "number_of_shards", None)
        sql = ''
        if clustered_by or number_of_shards:
            clustering = ' CLUSTERED'
            if clustered_by:
                sql += " BY ({})".format(self.quote_name(clustered_by))
            if number_of_shards:
                sql += " INTO {} SHARDS".format(number_of_shards)
        return sql

    def _partitioned_by_sql(self, model, params):
        partitioned_by = getattr(model._meta, "partitioned_by", None)
        if partitioned_by:
            return " PARTITIONED BY ({})".format(
                ", ".join((self.quote_name(p) for p in partitioned_by))
            )
        return ''

    def _table_settings_sql(self, model, params):
        number_of_replicas = getattr(model._meta, "number_of_replicas", None)
        refresh_interval = getattr(model._meta, "refresh_interval", None)
        table_settings = []

        if number_of_replicas is not None:
            table_settings.append("number_of_replicas=?")
            params.append(number_of_replicas)
        if refresh_interval is not None:
            table_settings.append("refresh_interval=?'")
            params.append(refresh_interval)

        if table_settings:
            return " WITH (" + ", ".join(table_settings) + ")"
        return ''

    def delete_model(self, model):
        super(DatabaseSchemaEditor, self).delete_model(model)

    def alter_db_table(self, model, old_db_table, new_db_table):
        raise NotImplementedError("cannot change the table name")

    def alter_db_tablespace(self, model, old_db_tablespace, new_db_tablespace):
        raise NotImplementedError("no tablespace support in crate")

    def add_field(self, model, field):
        return super(DatabaseSchemaEditor, self).add_field(model, field)

    def remove_field(self, model, field):
        raise NotImplementedError("removing fields is not implemented")

    def alter_field(self, model, old_field, new_field, strict=False):
        raise NotImplementedError("changing a field is not supported")

    def alter_unique_together(self, model, old_unique_together, new_unique_together):
        pass
