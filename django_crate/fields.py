from django.db import models

class ObjectField(models.Field):
    def db_type(self, connection):
        return 'object'
    def get_internal_type(self):
        return 'ObjectField'
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
    def from_db_value(self, value, expression, connection, context):
        return value or []
    def to_python(self, value):
        if not isinstance(value, list): raise self.ValidationError
        for v in value:
            if not isinstance(v, list): raise self.ValidationError
        return value or []
