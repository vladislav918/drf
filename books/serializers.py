from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from django.core.validators import MinValueValidator, MaxValueValidator

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .models import Book, ReadList, Genre, Author, Comment, Rating

from .documents import BookDocument


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id','title']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'content', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    class Meta:
        model = Rating
        fields = ['rating']


class BookSerializer(serializers.ModelSerializer):
    """
    Основной Serializers для книг
    """
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id','title', 'author', 'genre', 'description', 'cover_image']


class BookWithCommentSerializer(BookSerializer):
    """
    Serializers для отображения комментариев при просмотре конкретной книги
    """
    comments = serializers.SerializerMethodField()

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['comments']

    def get_comments(self, obj):
        queryset = Comment.objects.filter(book=obj.id).select_related('user').only('content', 'user__email', 'parent', 'created_at')
        serializer = CommentSerializer(queryset, many=True)
        return serializer.data


class ReadListSerializer(serializers.ModelSerializer):
    """
    Serializers для списка прочитанных книг
    """
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    book_details = BookSerializer(source='book', read_only=True)
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = ReadList
        fields = ['user', 'book', 'book_details']


class BookDocumentSerializer(DocumentSerializer):
    class Meta:
        document = BookDocument

        fields = ['id', 'title', 'author', 'genre', 'description']
