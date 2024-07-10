from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions, mixins

from .models import Book, ReadList, Author, Comment
from .serializers import (
        BookSerializer,
        ReadListSerializer,
        AuthorSerializer,
        CommentSerializer,
        BookWithCommentSerializer,
    )
from .filters import ReadBookListFilter


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс для отображения книг и добавления комментариев к конкретной книге
    """
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookWithCommentSerializer
        return BookSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comments(self, request, pk=None):
        book = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(book=book, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        book = self.get_object()
        comment_id = self.request.data.get('comment_id')

        if not comment_id:
            return Response({'error': 'comment_id is required'}, status=400)

        try:
            comment = book.comments.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=404)

        serializer = CommentSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save(book=book, user=self.request.user, parent=comment)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ReadListModelViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    Класс для отображения, добавления и удаления книг в список "Прочитанных"
    """
    serializer_class = ReadListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ReadBookListFilter

    def get_queryset(self):
        return ReadList.objects.filter(user=self.request.user)


    def create(self, request):
        serializer = ReadListSerializer(data=request.data)
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
