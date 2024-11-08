from books.domain.models import Book, Comment, Rating
from django.db.models import Prefetch


class BookRepository:

    @staticmethod
    def get_book_by_id(book_id):
        book = Book.objects.get(pk=book_id)
        return book

    @staticmethod
    def get_comment_on_book():
        queryset = Book.objects.all().select_related('genre').prefetch_related(
            'author',
            Prefetch(
                'comments', 
                queryset=Comment.objects.select_related('user').only('book_id' ,'content', 'parent_id', 'user__email', 'user__username', 'created_at')
            )
        )  
        return queryset

    @staticmethod
    def get_book():
        queryset = Book.objects.all().select_related('genre').prefetch_related('author').defer('description')
        return queryset


class CommentRepository:

    @staticmethod
    def create(book, user, parent, content):
        Comment.objects.create(book=book, user=user, parent=parent, content=content)

    @staticmethod
    def get_parent_id_for_comment(parent_id):
        parent = Comment.objects.get(pk=parent_id)
        return parent
    

class RatingRepository:

    @staticmethod
    def add_or_update_rating(book, user, rating_value):
        rating, created = Rating.objects.get_or_create(
            book=book,
            user=user,
            defaults={'rating': rating_value}
        )

        if not created:
            rating.rating = rating_value
            rating.save(update_fields=['rating'])

        return rating, created
