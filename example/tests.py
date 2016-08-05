"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase, override_settings
from django.conf import settings
from .models import Book, Author
import time

class BookCrateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BookCrateTest, cls).setUpClass()

    def setUp(self):
        Book.objects.all().delete()
        Author.objects.all().delete()

    def test_books_empty(self):
        self.assertEqual(Book.objects.all().count, 0)
