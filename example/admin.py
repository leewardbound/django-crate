from django.contrib import admin
from .models import Book, Author


# Register your models here.
class BookAdmin(admin.ModelAdmin):
    def num_author_books(self, obj):
        return obj.author.book_set.count()
    list_display = ['id', 'title', 'description', 'published', 'pages',
                    'author', 'num_author_books']

class AuthorAdmin(admin.ModelAdmin):
    def num_books(self, obj):
        return obj.book_set.count()
    list_display = ['name', 'num_books']

admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)

