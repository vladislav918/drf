from django.db import models
from django.db.models import Avg
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey


class Genre(models.Model):
    title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'{self.id} - {self.title}'


class Author(models.Model):
    name = models.CharField(max_length=90, unique=True)

    def __str__(self):
        return f'{self.name}'


class Comment(MPTTModel):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    level = models.IntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['content']

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'


class Rating(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], name='unique_rating_per_user')
        ]

    def __str__(self):
        return f"{self.user.username} оценил '{self.book.title}' как {self.rating}"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ManyToManyField(Author)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)

    def __str__(self):
        return f'{self.id} - {self.title}'


    def average_rating(self):
        ratings = self.rating_set.all()
        if ratings.exists():
            return ratings.aggregate(Avg('rating'))['rating__avg']
        return None


class ReadList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], name='unique_read_list_entry')
        ]

    def __str__(self):
        return f'{self.date_added} - {self.book}'
