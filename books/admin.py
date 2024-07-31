from django.contrib import admin

from .models import Book, Genre, ReadList, Author, Comment, Rating

from mptt.admin import MPTTModelAdmin


admin.site.register(Genre)


admin.site.register(Author)


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('content', 'book', 'user', 'created_at')
    list_filter = ('book',)


admin.site.register(Rating)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'genre', 'description', 'cover_image')
    filter_horizontal = ('author', )


@admin.register(ReadList)
class ReadListAdmin(admin.ModelAdmin):
    fields = ('book', 'user')
