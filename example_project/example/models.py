from __future__ import unicode_literals
from django.db import models
from datetime import datetime


import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

class Book(models.Model):
    id = models.CharField(max_length=1024, primary_key=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    published = models.DateTimeField(default=datetime.now)
    class Meta:
        in_db = 'local_crate'

