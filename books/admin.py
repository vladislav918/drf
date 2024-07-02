from django.contrib import admin


from .models import Book, Genre, ReadList


admin.site.register(Book)

admin.site.register(Genre)

admin.site.register(ReadList)

