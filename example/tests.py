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

    @classmethod
    def delete_everything(cls):
        Book.objects.all().delete()
        Author.objects.all().delete()
        cls.refresh_models()

    @classmethod
    def refresh_models(cls):
        refresh_model(Author)
        refresh_model(Book)

    def setUp(self):
        self.delete_everything()

    def test_create_book(self):
        self.assertEqual(Book.objects.all().count(), 0)
        Book.objects.create(author_id='123',
            title='my first book', pages=10)
        refresh_model(Book)
        self.assertEqual(Book.objects.all().count(), 1)

    def test_delete_book(self):
        Book.objects.create(author_id='123',
            title='my first book', pages=10)
        self.refresh_models()
        self.assertEqual(Book.objects.all().count(), 1)
        self.delete_everything()
        self.assertEqual(Book.objects.all().count(), 0)

    def test_book_title(self):
        Book.objects.create(author_id='123',
            title='my first book', pages=10)
        self.refresh_models()
        self.assertEquals(Book.objects.all()[0].title, 'my first book')

    def test_book_pages(self):
        Book.objects.create(author_id='123',
            title='my first book', pages=10)
        self.refresh_models()
        self.assertEquals(Book.objects.all()[0].pages, 10)

    def test_book_author_id(self):
        Book.objects.create(author_id='123',
            title='my first book', pages=10)
        self.refresh_models()
        self.assertEquals(Book.objects.all()[0].author_id, '123')

    def test_book_description(self):
        Book.objects.create(author_id='123',
            title='my first book', pages=10, description='a decent book')
        self.refresh_models()
        self.assertEquals(Book.objects.all()[0].description, 'a decent book')

    def test_many_books(self):
        for num in range (0, 100):
            Book.objects.create(author_id=str(num),
                title='my first book', pages=10)
        self.refresh_models()
        self.assertEquals(Book.objects.all().count(), 100)

    def test_create_author(self):
        self.assertEqual(Author.objects.all().count(), 0)
        Author.objects.create(name='Stephen King')
        refresh_model(Author)
        self.assertEqual(Author.objects.all().count(), 1)

    def test_delete_author(self):
        Author.objects.create(name='Stephen King')
        self.refresh_models()
        self.assertEqual(Author.objects.all().count(), 1)
        self.delete_everything()
        self.assertEqual(Author.objects.all().count(), 0)

    def test_author_name(self):
        Author.objects.create(name='Stephen King')
        refresh_model(Author)
        self.assertEqual(Author.objects.all()[0].name, 'Stephen King')

    def test_many_authors(self):
        for num in range (0, 100):
            Author.objects.create(name=num),
        self.refresh_models()
        self.assertEquals(Author.objects.all().count(), 100)
