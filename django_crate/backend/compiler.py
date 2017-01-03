# -*- coding: utf-8 -*-

import uuid
from django.db.models.sql import compiler
from ..util import milliseconds
from .creation import DatabaseCreation

TYPES = DatabaseCreation.data_types


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


class SQLInsertCompiler(compiler.SQLInsertCompiler):

    def prepare_value(self, field, value):
        opts = self.query.get_meta()
        pk_field = opts.pk
        if field == pk_field and not value:
            _type = TYPES.get(field.get_internal_type(), None)
            if _type == 'string':
                value = uuid.uuid4()
            else:
                raise Exception("Can't autopopulate primary key for type %s on " % (_type, field.model))

        return super(SQLInsertCompiler, self).prepare_value(field, value)

    def as_sql(self):
        opts = self.query.get_meta()
        pk_field = opts.pk
        if not self.query.fields:
            self.query.fields = []
        if not pk_field in self.query.fields:
            self.query.fields.append(pk_field)
        return super(SQLInsertCompiler, self).as_sql()


class SQLDeleteCompiler(compiler.SQLDeleteCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler):

    def as_sql(self):
        omit_updates = getattr(self.query.model, '__omit_update__', [])

        self.query.values = [(f, o, v) for (f, o, v) in self.query.values
                            if f.name not in omit_updates]

        return super(SQLUpdateCompiler, self).as_sql()


class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    pass
