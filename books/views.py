from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .models import Book, ReadList
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class ReadListViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = ReadList.objects.filter(user=request.user).values('book')
        books = Book.objects.filter(id__in=queryset)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


    def create(self, request):
        book_id = request.data.get('book_id')

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise NotFound("Книга не найдена.") 

        ReadList.objects.create(user=request.user, book=book)
        return Response({'message': 'Книга добавлена в список "Прочитанное"'})


    def destroy(self,request, pk=None):
        try:
            read_book = ReadList.objects.get(user=request.user, book_id=pk)
        except ReadList.DoesNotExist:
            raise NotFound("Книга не найдена в списке 'Прочитанное'.")

        read_book.delete()
        return Response({'message': 'Книга удалена из списка "Прочитанное"'})


