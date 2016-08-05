from __future__ import unicode_literals
from django.db import models
from datetime import datetime


import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)


class Author(models.Model):
    id = models.CharField(max_length=1024, primary_key=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        in_db = 'crate'

class Book(models.Model):
    id = models.CharField(max_length=1024, primary_key=True, blank=True)
    author = models.ForeignKey(Author)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    published = models.DateTimeField(default=datetime.now)
    pages = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return '%s by %s'%(self.title, self.author)

    class Meta:
        in_db = 'crate'
