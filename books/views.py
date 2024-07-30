from rest_framework.response import Response
from rest_framework import viewsets, status, mixins
from django.shortcuts import get_object_or_404

from .models import Book, ReadList, Author, Comment, Rating
from .serializers import (
    BookSerializer,
    ReadListSerializer,
    AuthorSerializer,
    CommentSerializer,
    BookWithCommentSerializer,
    RatingSerializer,
    BookDocumentSerializer
)
from .filters import ReadBookListFilter

from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import SearchFilterBackend, SuggesterFilterBackend

from .documents import BookDocument



class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс для отображения книг
    """
    queryset = Book.objects.all()
    permission_classes = []

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookWithCommentSerializer
        return BookSerializer


class CommentBookViewSet(viewsets.ViewSet):
    """
    Добавления комментариев к конкретной книге
    """
    queryset = Comment.objects.filter(parent=None)

    def create(self, request, book_pk=None):
        book = get_object_or_404(Book, pk=book_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            parent_id = request.data.get('parent')
            parent = None
            if parent_id:
                parent = get_object_or_404(Comment, pk=parent_id)
            serializer.save(book=book, user=request.user, parent=parent)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class RatingViewSet(viewsets.ViewSet):
    """
    Добавления рейтинга к конкретной книге
    """
    def create(self, request, book_pk=None):
        book = get_object_or_404(Book, pk=book_pk)

        serializer = RatingSerializer(data=self.request.data)
        if serializer.is_valid():
            rating, created = Rating.objects.update_or_create(
                book=book,
                user=request.user,
                defaults={'rating': serializer.validated_data['rating']}
            )
            if not created:
                return Response({'message': 'Рейтинг обновлен'}, status=status.HTTP_200_OK)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ReadListModelViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    Класс для отображения, добавления и удаления книг в список "Прочитанных"
    """
    serializer_class = ReadListSerializer
    filterset_class = ReadBookListFilter

    def get_queryset(self):
        return ReadList.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = ReadListSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        if ReadList.objects.filter(
                user=request.user,
                book=serializer.validated_data['book']
            ).exists():

            return Response(
                {'error': 'Эта книга уже добавлена в список "Прочитанное"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def destroy(self, request, pk=None):
        read_book = ReadList.objects.filter(user=request.user, book_id=pk)

        if read_book.exists():
            read_book.delete()
            return Response({'message': 'Книга удалена из списка "Прочитанное"'})

        return Response({'error': 'Книга не найдена'})


class AuthorDetailView(viewsets.ReadOnlyModelViewSet):
    """
    Класс для отображения Авторов книг и книг, которые они написали
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def retrieve(self, request, pk=None):
        author = self.get_object()

        books = author.book_set.all()
        books_serializer = BookSerializer(books, many=True)

        return Response(books_serializer.data)


class BookDocumentView(DocumentViewSet):
    """
    Поиск через ElasticSearch 
    """
    permission_classes = []
    document = BookDocument
    serializer_class = BookDocumentSerializer

    filter_backends = [
    	SearchFilterBackend,
        SuggesterFilterBackend,
    ]

    search_fields = ('title',)

    suggester_fields = {
        'title': {
            'field': 'title.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }
