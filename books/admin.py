from django.contrib import admin

from .models import Book, Genre, ReadList, Author, Comment, Rating


admin.site.register(Genre)

admin.site.register(Author)

admin.site.register(Comment)

admin.site.register(Rating)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'genre', 'description', 'cover_image')
    filter_horizontal = ('author', )


@admin.register(ReadList)
class ReadListAdmin(admin.ModelAdmin):
    fields = ('book', 'user')
