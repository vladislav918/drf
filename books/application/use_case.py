from .commands import CommentBookCommand, CreateRatingCommand
from accounts.infrastructure.repositories import UserRepository

from books.infrastructure.repositories import BookRepository, CommentRepository, RatingRepository


class CreateCommentBookUseCase:

    def execute(self, command: CommentBookCommand):
        book = BookRepository.get_book_by_id(command.book_pk)
        user = UserRepository.get_user_model_instance(command.user_id)

        parent = None
        if command.parent_id:
            parent = CommentRepository.get_parent_id_for_comment(command.parent_id)
        
        CommentRepository.create(book=book, user=user, content=command.content, parent=parent)


class CreateRatingUseCase:

    def execute(self, command: CreateRatingCommand):
        book = BookRepository.get_book_by_id(command.book_pk)
        user = UserRepository.get_user_model_instance(command.user_id)

        return RatingRepository.add_or_update_rating(book=book, user=user, rating_value=command.rating)