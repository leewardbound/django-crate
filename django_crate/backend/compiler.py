# -*- coding: utf-8 -*-

from django.db.models.sql import compiler
from datetime import datetime, time, date
from django_crate.util import milliseconds
from .creation import DatabaseCreation
TYPES = DatabaseCreation.data_types
import uuid
import time as time_lib
import json

class SQLCompiler(compiler.SQLCompiler):
    def get_converters(self, expressions):
        converters = {}
        for i, expression in enumerate(expressions):
            if expression:
                backend_converters = self.connection.ops.get_db_converters(expression)
                field_converters = expression.get_db_converters(self.connection)
                if backend_converters or field_converters:
                    converters[i] = (backend_converters + field_converters, expression)
        return converters

    def execute_sql(self, *args, **kwargs):
        return super(SQLCompiler, self).execute_sql(*args, **kwargs)

    def as_sql(self):
        sql = super(SQLCompiler, self).as_sql()
        return sql


class SQLInsertCompiler(compiler.SQLInsertCompiler):
    def prepare_value(self, field, value):
        opts = self.query.get_meta()
        pk_field = opts.pk
        if field == pk_field and not value:
            _type = TYPES.get(field.get_internal_type(), None)
            if _type == 'string':
                value = '%d-%s'%(milliseconds(), uuid.uuid4())
            elif _type == 'long':
                value = milliseconds()
            else:
                raise Exception("Can't autopopulate primary key for type %s on "%(_type, field.model))

        return super(SQLInsertCompiler, self).prepare_value(field, value)

    def as_sql(self):
        opts = self.query.get_meta()
        pk_field = opts.pk
        if not self.query.fields: self.query.fields = []
        if not pk_field in self.query.fields:
            self.query.fields.append(pk_field)
        sql = super(SQLInsertCompiler, self).as_sql()
        return sql

class SQLDeleteCompiler(compiler.SQLDeleteCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler):
    def as_sql(self):
        opts = self.query.get_meta()
        pk_field = opts.pk
        omit_updates = getattr(self.query.model, '__omit_update__', [])

        self.query.values = [(f, o, v) for (f, o, v) in self.query.values
                            if f.name not in omit_updates]
        if omit_updates: raise

        return super(SQLUpdateCompiler, self).as_sql()


class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    pass
