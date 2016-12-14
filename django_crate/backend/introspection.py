from __future__ import unicode_literals

from collections import namedtuple

from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection, FieldInfo, TableInfo,
)
from django.utils.encoding import force_text

FieldInfo = namedtuple('FieldInfo', FieldInfo._fields + ('default',))


class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Maps type codes to Django Field types.
    data_types_reverse = {
        "boolean": "BooleanField",
        "byte": "SmallIntegerField",
        "short": "SmallIntegerField",
        "integer": "IntegerField",
        "long": "BigIntegerField",
        "float": "FloatField",
        "double": "FloatField",  # no double type in python
        "timestamp": "DateTimeField",
        "ip": "IPAddressField",
        "string": "CharField",
        # TODO: object and array
    }

    def get_field_type(self, data_type, description):
        # TODO
        return super(DatabaseIntrospection, self).get_field_type(data_type, description)

    def get_table_list(self, cursor):
        cursor.execute("""
            SELECT table_name AS relname, 't' AS relkind
            FROM information_schema.tables
            WHERE table_schema NOT IN ('sys', 'blob', 'information_schema', 'pg_catalog')
              AND table_schema = CURRENT_SCHEMA()""")
        return [TableInfo(*row) for row in cursor.fetchall()]

    def get_table_description(self, cursor, table_name):
        cursor.execute("""
            SELECT column_name, is_nullable, NULL AS column_default
            FROM information_schema.columns
            WHERE table_name = ?
              AND table_schema = CURRENT_SCHEMA()""", [table_name])
        field_map = {line[0]: line[1:] for line in cursor.fetchall()}
        cursor.execute('SELECT * FROM {} LIMIT 1'.format(self.connection.ops.quote_name(table_name)))
        return [
            FieldInfo(*(
                (force_text(line[0]),) +
                line[1:6] +
                (field_map[force_text(line[0])][0] == 'YES', field_map[force_text(line[0])][1])
            )) for line in cursor.description
        ]

    def sequence_list(self):
        return []

    def get_relations(self, cursor, table_name):
        return {}

    def get_key_columns(self, cursor, table_name):
        return []

    def get_indexes(self, cursor, table_name):
        cursor.execute("""SELECT column_name, column_name = any(constraint_name) AS is_primary
        FROM information_schema.columns col,
             information_schema.table_constraints con
        WHERE con.table_name = col.table_name
          AND col.table_name = ?
          AND col.table_schema = CURRENT_SCHEMA()""", [table_name])
        indexes = {}
        for col_name, is_primary in cursor.fetchall():
            indexes[col_name] = {
                'primary_key': is_primary,
                'unique': True
            }
        return indexes

    def get_constraints(self, cursor, table_name):
        cursor.execute("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name = ?
          AND table_schema = CURRENT_SCHEMA()""", [table_name])
        constraints = {}
        for columns, kind in cursor.fetchall():
            name = "__".join([table_name] + columns)
            # If we're the first column, make the record
            if name not in constraints:
                constraints[constraint] = {
                    "columns": columns,
                    "primary_key": kind.lower() == "primary_key",
                    "unique": kind.lower() in ["primary_key", "unique"],
                    "foreign_key": None,
                    "check": False,
                    "index": False,
                }
        return constraints
