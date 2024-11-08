from django.db.models import Prefetch
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    SearchFilterBackend, SuggesterFilterBackend)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from books.documents import BookDocument
from books.filters import ReadBookListFilter
from books.domain.models import Author, Book, Rating, ReadList
from books.api.serializers import (AuthorSerializer, BookDocumentSerializer,
                          BookSerializer, BookWithCommentSerializer,
                          CommentSerializer, RatingSerializer,
                          ReadListSerializer)


from books.application.commands import CommentBookCommand, CreateRatingCommand
from books.application.use_case import CreateCommentBookUseCase, CreateRatingUseCase
from books.infrastructure.repositories import BookRepository
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page



class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс для отображения книг
    """

    permission_classes = []

    # @method_decorator(cache_page(60 * 15))
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    # @method_decorator(cache_page(60 * 15))
    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = BookRepository.get_book()
        if self.action == 'retrieve':
            queryset = BookRepository.get_comment_on_book()
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookWithCommentSerializer
        return BookSerializer


class CommentBookAPIView(APIView):
    """
    Добавление комментариев к конкретной книге
    """
    serializer_class = CommentSerializer

    def post(self, request, book_pk=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            command = CommentBookCommand(
                book_pk=book_pk,
                parent_id=request.data.get('parent'),
                user_id=request.user.id,
                content=serializer.validated_data['content'],
            )

            use_case = CreateCommentBookUseCase()
            use_case.execute(command)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingAPIView(APIView):
    """
    Добавления рейтинга к конкретной книге
    """
    serializer_class = RatingSerializer

    def post(self, request, book_pk=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            command = CreateRatingCommand(
                book_pk=book_pk,
                user_id=request.user.id,
                rating=serializer.validated_data['rating'],
            )

            use_case = CreateRatingUseCase()
            rating, created = use_case.execute(command)

            if not created:
                return Response({'message': 'Рейтинг обновлен'}, status=status.HTTP_200_OK)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return ReadList.objects.filter(user=self.request.user).select_related(
            'book').select_related('book__genre').prefetch_related('book__author')

    def create(self, request):
        serializer = ReadListSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

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
    queryset = Author.objects.all().prefetch_related(
        Prefetch('book_set', queryset=Book.objects.select_related('genre'))
    )
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

    filter_backends = [SearchFilterBackend, SuggesterFilterBackend]

    search_fields = ('title',)

    suggester_fields = {
        'title': {
            'field': 'title.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }
