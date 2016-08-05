"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase, override_settings
from django.conf import settings
from django.test import TransactionTestCase
from .models import Book, Author
from django_crate.util import refresh_model, wait_until_exists
import time

class BookCrateTest(TestCase):
    def delete_everything(self):
        Book.objects.all().delete()
        Author.objects.all().delete()
        self.refresh_models()

    def refresh_models(self):
        refresh_model(Author)
        refresh_model(Book)


    def test_create_book(self):
        self.delete_everything()
        self.assertEqual(Book.objects.all().count(), 0)
        book=Book.objects.create(id='hi',
            title='my first book', pages=10)
        qs = wait_until_exists(lambda: Book.objects.all(), 'hi')
        assert(qs.get(pk='hi'))

    def test_fk_create(self):
        self.delete_everything()
        Author.objects.create(id='456', name='first_author')
        Book.objects.create(id='xyz', author_id='456', title='my first book', pages=10)

        qs = wait_until_exists(lambda: Book.objects.all(), 'xyz')
        self.assertEqual(qs.get(pk='xyz').author.name, 'first_author')
        #self.assertEqual(Book.objects.filter(author__name='first_author').count(), 1)

    def test_fk_filter_select(self):
        self.delete_everything()
        author = Author.objects.create(id='123', name='first_author')
        book = Book.objects.create(id='abc', author_id='123', title='my first book', pages=10)

        wait_until_exists(lambda: Author.objects.all(), '123')
        qs = wait_until_exists(lambda: Book.objects.all(), 'abc')
        assert(qs.filter(author__name='first_author').get())
        with self.assertRaises(Book.DoesNotExist):
            qs.exclude(author__name='first_author').get()
        #self.assertEqual(Book.objects.filter(author__name='first_author').count(), 1)

