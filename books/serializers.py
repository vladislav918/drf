from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Book, ReadList, Genre, Author


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['title']


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ['id', 'name']


class BookWithoutAuthorSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['title', 'genre', 'description', 'cover_image', 'rating']


class BookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    author = AuthorSerializer(many=True, read_only=True)
    
    class Meta: 
        model = Book
        fields = ['title', 'author', 'genre', 'description', 'cover_image', 'rating']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ReadListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)
    book_details = BookSerializer(source='book', read_only=True)

    class Meta:
        model = ReadList
        fields = ['user', 'book', 'date_added', 'book_details']
