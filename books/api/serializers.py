from django.core.validators import MaxValueValidator, MinValueValidator
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from rest_framework import serializers

from ..documents import BookDocument
from ..domain.models import Author, Book, Comment, Genre, Rating, ReadList

from accounts.api.serializers import UserSerializer


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'title']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'content', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        model = Rating
        fields = ['rating']


class BookSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для книг
    """
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'cover_image']


class BookWithCommentSerializer(BookSerializer):
    """
    Сериализатор для отображения книги с комментариями
    """
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['comments']


class ReadListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка прочитанных книг
    """
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    book_details = BookSerializer(source='book', read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ReadList
        fields = ['user', 'book', 'book_details']


class BookDocumentSerializer(DocumentSerializer):
    """
    Сериализатор для поиска книг через Elasticsearch
    """
    class Meta:
        document = BookDocument
        fields = ['id', 'title', 'author', 'genre', 'description']