from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import Book, ReadList, Genre, Author, Comment


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
        if obj.parent is None:
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class BookWithCommentSerializer(serializers.ModelSerializer):
    """
    Serializers для отображения комментариев при просмотре конкретной книги
    """
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'description', 'comments', 'cover_image', 'rating']


class BookSerializer(serializers.ModelSerializer):
    """
    Основной Serializers для книг
    """
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id','title', 'author', 'genre', 'description', 'cover_image', 'rating']


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
