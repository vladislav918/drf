from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book, Author, Genre
from books.serializers import BookSerializer, BookWithCommentSerializer


class BookViewSetTest(APITestCase):
    def setUp(self):
        # Создание тестовых данных
        self.author1 = Author.objects.create(name='Автор 1')
        self.author2 = Author.objects.create(name='Автор 2')
        self.genre1 = Genre.objects.create(title='Жанр 1')
        self.book1 = Book.objects.create(
            title='Книга 1',
            genre=self.genre1,
            description='Описание книги 1',
        )

        self.book1.author.set([self.author1, self.author2])

    def test_list_books(self):
        """Проверка вывода списка книг"""
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Книга 1')

    def test_retrieve_book(self):
        """Проверка получения информации о конкретной книге"""
        response = self.client.get(f'/books/{self.book1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Книга 1')
        self.assertEqual(response.data['author'][0]['name'], 'Автор 1')
        self.assertEqual(response.data['author'][1]['name'], 'Автор 2')
        self.assertEqual(response.data['genre']['name'], 'Жанр 1')
        self.assertEqual(response.data['description'], 'Описание книги 1')

        # Проверка использования BookWithCommentSerializer
        self.assertIsInstance(response.data, dict)
        self.assertIn('comments', response.data)
        self.assertIsInstance(response.data['comments'], list)

    def test_get_serializer_class(self):
        """Проверка выбора правильного сериализатора в зависимости от действия"""
        view = BookViewSet()
        view.action = 'retrieve'
        self.assertEqual(view.get_serializer_class(), BookWithCommentSerializer)

        view.action = 'list'
        self.assertEqual(view.get_serializer_class(), BookSerializer)
