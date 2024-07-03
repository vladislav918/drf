from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.id} - {self.title}'


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=60)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    def __str__(self):
        return f'{self.id} - {self.title}'


class ReadList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.date_added} - {self.book}'
