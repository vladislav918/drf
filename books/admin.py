from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.db import models

from .models import Book, Genre, ReadList, Author


admin.site.register(Genre)

admin.site.register(Author)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'genre', 'description', 'cover_image', 'rating')
    filter_horizontal = ('author', )


@admin.register(ReadList)
class ReadListAdmin(admin.ModelAdmin):
    fields = ('book', 'user')
