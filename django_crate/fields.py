from django.db import models

class StringArrayAny(models.Lookup):
    lookup_name = 'any'
    function = 'ANY'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = compiler.compile(self.lhs)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = rhs_params + lhs_params
        return '%s = ANY(%s)' % (rhs, lhs), params

class ObjectField(models.Field):
    def db_type(self, connection):
        return 'object'
    def get_internal_type(self):
        return 'ObjectField'
    def get_prep_value(self, value):
        return value or {}
    def from_db_value(self, value, expression, connection, context):
        return value or {}
    def to_python(self, value):
        if not isinstance(value, dict): raise self.ValidationError
        return value or {}

class StringArrayField(models.Field):
    def db_type(self, connection):
        return 'array(string)'
    def get_internal_type(self):
        return 'StringArrayField'
    def get_prep_value(self, value):
        return value or []
    def from_db_value(self, value, expression, connection, context):
        return value or []
    def to_python(self, value):
        if not isinstance(value, list): raise self.ValidationError
        for v in value:
            if not isinstance(v, list): raise self.ValidationError
        return value or []
StringArrayField.register_lookup(StringArrayAny)

class ObjectArrayField(models.Field):
    def db_type(self, connection):
        return 'array(object)'
    def get_internal_type(self):
        return 'ObjectArrayField'
    def get_prep_value(self, value):
        return value or []
    def from_db_value(self, value, expression, connection, context):
        return value or []
    def to_python(self, value):
        if not isinstance(value, list): raise self.ValidationError
        for v in value:
            if not isinstance(v, list): raise self.ValidationError
        return value or []
