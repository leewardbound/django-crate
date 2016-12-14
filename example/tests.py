"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import time
from django.conf import settings
from django.db import connections
from django.test import TestCase, override_settings
from .models import Book, Author


def refresh_model(model, schema='test_'):
    sql = 'refresh table "{}"'.format(model._meta.db_table)
    conn = connections[getattr(model._meta, 'in_db', 'default')]
    with conn.cursor() as cursor:
        cursor.execute(sql)


class BookCrateTest(TestCase):

    def delete_everything(self):
        self.refresh_models()
        Book.objects.all().delete()
        Author.objects.all().delete()
        self.refresh_models()

    def refresh_models(self):
        refresh_model(Author)
        refresh_model(Book)

    def setUp(self):
        super(BookCrateTest, self).setUp()
        self.delete_everything()

    def tearDown(self):
        self.delete_everything()
        super(BookCrateTest, self).tearDown()

    def test_create_book(self):
        Book.objects.create(id='hi', title='my first book', pages=10)
        assert(Book.objects.get(pk='hi'))

    def test_fk_create(self):
        author = Author.objects.create(id='456', name='first_author')
        book = Book.objects.create(id='xyz', author_id=author.id, title='my first book', pages=10)
        qs = Book.objects.get(pk=book.id)
        self.assertEqual(qs.author.name, 'first_author')

    def test_fk_filter_select(self):
        author = Author.objects.create(id='123', name='first_author')
        book = Book.objects.create(id='abc', author=author, title='my first book', pages=10)
        self.refresh_models()
        qs = Book.objects
        assert(qs.filter(author__name='first_author').get())
        with self.assertRaises(Book.DoesNotExist):
            qs.exclude(author__name='first_author').get()

    def test_delete_book(self):
        pk = 'delete_test'
        Book.objects.create(id=pk, title='my first book', pages=10)
        book = Book.objects.get(pk=pk)
        assert(book.id == pk)
        self.delete_everything()
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(pk=pk)

    def test_book_attrs(self):
        Book.objects.create(author_id='123',
            title='my first book', pages=10, description='a decent book')
        self.refresh_models()
        qs = Book.objects.all()
        self.assertEquals(qs[0].title, 'my first book')
        self.assertEquals(qs[0].pages, 10)
        self.assertEquals(qs[0].description, 'a decent book')

    def test_create_author(self):
        self.assertEqual(Author.objects.all().count(), 0)
        Author.objects.create(id='steve', name='Stephen King')
        steve = Author.objects.get(pk='steve')
        self.assertEqual(steve.name, 'Stephen King')
        steve.delete()
        self.refresh_models()
        self.assertEqual(Author.objects.all().count(), 0)

    def test_many_books(self):
        for num in range (0, 100):
            Book.objects.create(pk='pk{}'.format(num),
                                title='book {}'.format(num),
                                pages=num+10),
        self.refresh_models()
        self.assertEquals(Book.objects.all().count(), 100)

    def test_many_authors(self):
        for num in range (0, 100):
            Author.objects.create(pk='pk{}'.format(num),
                                  name='author {}'.format(num)),
        self.refresh_models()
        self.assertEquals(Author.objects.all().count(), 100)
