"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase, override_settings
from django.conf import settings
from django.test import TransactionTestCase
from .models import Book, Author
from django_crate.util import refresh_model
import time

class BookCrateTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BookCrateTest, cls).setUpClass()
        cls.main_auth = Author.objects.create(name='first')
        cls.main_book = Book.objects.create(
            author_id=cls.main_auth.id,
            title='my first book', pages=10)

    def delete_everything(self):
        Book.objects.all().delete()
        Author.objects.all().delete()
        self.refresh_models()

    def refresh_models(self):
        refresh_model(Author)
        refresh_model(Book)

    def setUp(self):
        self.delete_everything()

    def test_create_book(self):

        self.assertEqual(Book.objects.all().count(), 0)

        Book.objects.create(author_id='123',
            title='my first book', pages=10)

        self.refresh_models()

        self.assertEqual(Book.objects.all().count(), 1)
