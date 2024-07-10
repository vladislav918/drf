from django.contrib import admin

from .models import Book, Genre, ReadList, Author, Comment


admin.site.register(Genre)

admin.site.register(Author)

admin.site.register(Comment)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'genre', 'description', 'cover_image', 'rating')
    filter_horizontal = ('author', )


@admin.register(ReadList)
class ReadListAdmin(admin.ModelAdmin):
    fields = ('book', 'user')
