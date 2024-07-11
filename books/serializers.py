from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import Book, ReadList, Genre, Author, Comment, Rating
from django.core.validators import MinValueValidator, MaxValueValidator


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['title']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    created_at = serializers.DateTimeField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['content', 'user', 'created_at', 'replies']

    def get_replies(self, obj):
        replies = obj.replies.all()
        if replies.exists():
            return CommentSerializer(replies, many=True).data
        return []


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


class BookWithCommentSerializer(serializers.ModelSerializer):
    """
    Serializers для отображения комментариев при просмотре конкретной книги
    """
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, required=False)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'description', 'comments', 'average_rating','cover_image']

    def get_average_rating(self, obj):
        return obj.average_rating()


class BookSerializer(serializers.ModelSerializer):
    """
    Основной Serializers для книг
    """
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id','title', 'author', 'genre', 'description', 'cover_image']


class ReadListSerializer(serializers.ModelSerializer):
    """
    Serializers для списка прочитанных книг
    """
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)
    book_details = BookSerializer(source='book', read_only=True)
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = ReadList
        fields = ['user', 'book', 'book_details']
