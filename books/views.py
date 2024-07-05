from rest_framework.response import Response
from rest_framework import viewsets, status, permissions, mixins

from .models import Book, ReadList
from .serializers import BookSerializer, ReadListSerializer
from .filters import ReadBookListFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


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
