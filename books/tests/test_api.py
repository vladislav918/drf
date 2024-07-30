from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from books.serializers import BookSerializer, BookWithCommentSerializer, AuthorSerializer
from books.views import BookViewSet, ReadListModelViewSet
from books.models import Book, Author, Genre, Comment, Rating, ReadList

from accounts.models import User


class BookSetupMixin:
    def setUp(self):
        super().setUp()
        self.genre = Genre.objects.create(title='Test Genre')
        self.author = Author.objects.create(name='Test Author')
        self.book = Book.objects.create(title='Test Book', genre=self.genre)
        self.book.author.add(self.author)


class UserSetupMixin:
    def setUp(self):
        super().setUp()
        self.client_authenticated = APIClient()
        self.client_unauthenticated = APIClient()
        self.user = User.objects.create_user(
            email='testuser@testuser.ru',
            username='testuser',
            password='testpassword'
        )
        self.client_authenticated.force_authenticate(user=self.user)


class BookViewSetTestCase(UserSetupMixin, BookSetupMixin, APITestCase):
    def test_list_view_returns_all_books(self):
        """
        Тест для проверки количества книг.
        """
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Book.objects.count())


    # def test_retrieve_view_returns_correct_details(self):
    #     """
    #     Тест для просмотра детально книг
    #     """
    #     comment = Comment.objects.create(
    #         book=self.book,
    #         user=self.user,
    #         content="Пример комментария",
    #     )
    #     url = reverse('book-detail', kwargs={'pk': self.book.pk})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     expected_data = BookWithCommentSerializer(self.book).data
    #     print("Response Data:", response.data)
    #     print("Expected Data:", expected_data)
    #     self.assertEqual(response.data, expected_data)


    def test_get_serializer_class_for_retrieve(self):
        """
        Тест для проверки какой сериализатор используется
        """
        request = reverse('book-detail', kwargs={'pk': self.book.pk})
        view = BookViewSet()
        view.request = request
        view.action = 'retrieve'
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, BookWithCommentSerializer)


    def test_get_serializer_class_for_list(self):
        """
        Тест для проверки какой сериализатор используется
        """
        request = self.client.get(reverse('book-list'))
        view = BookViewSet()
        view.request = request
        view.action = 'list'
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, BookSerializer)


class CommentBookViewSetTests(UserSetupMixin, BookSetupMixin, APITestCase):
    def test_create_comment(self):
        """
        Тест создания комментария к книге.
        """
        data = {
            'content': 'Test comment',
        }

        url = reverse('comment-list', kwargs={'book_pk': self.book.pk})
        response = self.client_authenticated.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()
        self.assertEqual(comment.book, self.book)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'Test comment')


    def test_create_comment_with_parent(self):
        """
        Тест создания комментария с родителем.
        """
        parent_comment = Comment.objects.create(
            book = self.book,
            user = self.user,
            content = 'Parent comment',
        )
        data = {
            'content': 'Reply comment',
            'parent': parent_comment.pk,
        }

        url = reverse('comment-list', kwargs={'book_pk': self.book.pk})
        response = self.client_authenticated.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

        comment = Comment.objects.last()
        self.assertEqual(comment.book, self.book)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'Reply comment')
        self.assertEqual(comment.parent, parent_comment)


    def test_create_comment_invalid_data(self):
        """
        Тест создания комментария с невалидными данными.
        """
        data = {
            'content': '',
        }
        url = reverse('comment-list', kwargs={'book_pk': self.book.pk})
        response = self.client_authenticated.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.count(), 0)


    def test_create_comment_invalid_parent(self):
        """
        Тест создания комментария с невалидным родителем.
        """
        data = {
            'content': 'Reply comment',
            'parent': 9999,
        }
        url = reverse('comment-list', kwargs={'book_pk': self.book.pk})
        response = self.client_authenticated.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Comment matches the given query.')
        self.assertEqual(Comment.objects.count(), 0)


class RatingViewSetTest(UserSetupMixin, BookSetupMixin, APITestCase):
    def test_create_rating(self):
        """
        Тест для проверки создания рейтинга
        """
        data = {'rating': 4}
        url = f'/api/v1/book/{self.book.pk}/ratings/'
        response = self.client_authenticated.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.first().rating, 4)


    def test_update_rating(self):
        """
        Тест для проверки обновления рейтинга
        """
        rating = Rating.objects.create(
            book=self.book, user=self.user, rating=3
        )

        data = {'rating': 5}
        url = f'/api/v1/book/{self.book.pk}/ratings/'
        response = self.client_authenticated.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.first().rating, 5)


    def test_create_rating_unauthorized(self):
        """
        Тест для проверки создания рейтинга неавторизованным пользователем
        """
        data = {'rating': 4}
        url = f'/api/v1/book/{self.book.pk}/ratings/'
        response = self.client_unauthenticated.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_invalid_data(self):
        """
        Тест для проверки создания рейтинга с невалидными данными
        """
        data = {'rating': 'invalid'}
        url = f'/api/v1/book/{self.book.pk}/ratings/'
        response = self.client_authenticated.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)


    def test_nonexistent_book(self):
        """
        Тест для проверки создания рейтинга для несуществующей книги
        """
        data = {'rating': 4}
        response = self.client_authenticated.post(
            f'/book/999/ratings/', data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReadListModelViewSetTests(UserSetupMixin, BookSetupMixin, APITestCase):
    def test_get_queryset(self):
        """
        Тест на проверку модели
        """
        viewset = ReadListModelViewSet()
        request = self.client_authenticated.get('/read-list/')
        viewset.request = request
        request.user = self.user

        queryset = viewset.get_queryset()
        self.assertEqual(queryset.model, ReadList)
        self.assertEqual(list(queryset), [])


    def test_create_read_list_entry(self):
        """
        Тест на проверку создания прочитанных книг
        """
        data = {'book': self.book.id}
        url = '/api/v1/read-book/'
        response = self.client_authenticated.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReadList.objects.count(), 1)
        self.assertEqual(ReadList.objects.first().user, self.user)
        self.assertEqual(ReadList.objects.first().book, self.book)


    def test_create_duplicate_read_list_entry(self):
        """
        Тест на проверку дубликов
        """
        self.client_authenticated.post('/api/v1/read-book/', {'book': self.book.id}, format='json')
        response = self.client_authenticated.post('/api/v1/read-book/', {'book': self.book.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ReadList.objects.count(), 1)


    def test_delete_read_list_entry(self):
        """
        Тест на удаления книги из прочитанных
        """
        read_list_entry = ReadList.objects.create(user=self.user, book=self.book)
        response = self.client_authenticated.delete(f'/api/v1/read-book/{read_list_entry.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ReadList.objects.filter(id=read_list_entry.id).exists())


    def test_delete_nonexistent_read_list_entry(self):
        """
        Тест на удаления книги из прочитанных не существующей книги
        """
        response = self.client_authenticated.delete('/read-list/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_list_read_list_entries(self):
        """
        Тест на получения всех добавленных прочитанных книг
        """
        read_list_entry = ReadList.objects.create(user=self.user, book=self.book)
        url = '/api/v1/read-book/'
        response = self.client_authenticated.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_details']['id'], self.book.id)


class AuthorDetailViewTests(BookSetupMixin, UserSetupMixin, APITestCase):
    def test_get_author_details(self):
        """
        Проверяет, что API возвращает детали автора и список его книг.
        """
        url = reverse('author-detail', args=[self.author.pk])
        response = self.client_authenticated.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['author'][0]['name'], self.author.name) 


    def test_author_serializer(self):
        """
        Проверяет, что AuthorSerializer сериализует данные автора правильно.
        """
        serializer = AuthorSerializer(self.author)
        self.assertEqual(serializer.data['name'], self.author.name)


    def test_book_serializer(self):
        """
        Проверяет, что BookSerializer сериализует данные книги правильно.
        """
        serializer = BookSerializer(self.book)
        self.assertEqual(serializer.data['title'], self.book.title)
        self.assertEqual(serializer.data['author'][0]['name'], self.author.name)
