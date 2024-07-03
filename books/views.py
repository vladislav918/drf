from rest_framework.response import Response
from rest_framework import viewsets, status, permissions

from .filters import ReadBookListFilter
from .models import Book, ReadList
from .serializers import BookSerializer, ReadListSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class ReadListModelViewSet(viewsets.ModelViewSet):
    """
    Класс для отображения, добавления и удаления книг в список "Прочитанных"
    """
    queryset = ReadList.objects.all()
    serializer_class = ReadListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReadList.objects.filter(user=self.request.user)


    def create(self, request):
        book_id = request.data.get('book')
        if not book_id:
            return Response(
                {'error': 'Не указан ID книги'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Книга не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        if ReadList.objects.filter(user=request.user, book=book).exists():
            return Response(
                {'error': 'Эта книга уже добавлена в список "Прочитанное"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ReadList.objects.create(user=request.user, book=book)
        return Response({'message': 'Книга добавлена в список "Прочитанное"'})


    def destroy(self,request, pk=None):
        try:
            read_book = ReadList.objects.get(user=request.user, book_id=pk)
        except ReadList.DoesNotExist:
            return Response(
                {'error': 'Книга не найдена в списке "Прочитанное"'},
                status=status.HTTP_404_NOT_FOUND
            )

        read_book.delete()
        return Response({'message': 'Книга удалена из списка "Прочитанное"'})
