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
        author = wait_until_exists(lambda: Author.objects.all(), '123').get(pk='123')
        book = Book.objects.create(id='abc', author=author, title='my first book', pages=10)

        qs = wait_until_exists(lambda: Book.objects.all(), 'abc')
        time.sleep(1)
        self.refresh_models()
        assert(qs.filter(author__name='first_author').get())
        with self.assertRaises(Book.DoesNotExist):
            qs.exclude(author__name='first_author').get()
        #self.assertEqual(Book.objects.filter(author__name='first_author').count(), 1)

    def test_delete_book(self):
        self.delete_everything()
        Book.objects.create(id='delete_test', title='my first book', pages=10)
        qs = wait_until_exists(lambda: Book.objects.all(), 'delete_test')
        assert(qs.get(pk='delete_test'))
        self.delete_everything()
        with self.assertRaises(Book.DoesNotExist):
            qs.filter(pk='delete_test').get()

    def test_book_attrs(self):
        self.delete_everything()
        Book.objects.create(author_id='123',
            title='my first book', pages=10, description='a decent book')
        qs = wait_until_exists(lambda: Book.objects.all(), 'delete_test')
        self.assertEquals(Book.objects.all()[0].title, 'my first book')
        self.assertEquals(Book.objects.all()[0].pages, 10)
        self.assertEquals(Book.objects.all()[0].description, 'a decent book')


    def test_create_author(self):
        self.delete_everything()
        self.assertEqual(Author.objects.all().count(), 0)
        Author.objects.create(id='steve', name='Stephen King')
        qs = wait_until_exists(lambda: Author.objects.all(), 'steve')
        self.assertEqual(qs.get(pk='steve').name, 'Stephen King')
        qs.get(pk='steve').delete()
        self.refresh_models()
        self.assertEqual(Author.objects.all().count(), 0)

    def test_many_books(self):
        self.delete_everything()
        for num in range (0, 100):
            Book.objects.create(pk='many-%s'%num, title='book %s'%num, pages=10)
        time.sleep(2) #sigh, eventual consistency...
        self.refresh_models()
        self.assertEquals(Book.objects.all().count(), 100)

    def test_many_authors(self):
        self.delete_everything()
        self.refresh_models()
        for num in range (0, 100):
            Author.objects.create(pk='many-%s'%num, name='author %s'%num),
        time.sleep(2) #sigh, eventual consistency...
        self.refresh_models()
        self.assertEquals(Author.objects.all().count(), 100)
