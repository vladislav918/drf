from dataclasses import dataclass


@dataclass
class CommentBookCommand:
    book_pk: int
    parent_id: int
    user_id: int
    content: str


@dataclass
class CreateRatingCommand:
    book_pk: int
    user_id: int
    rating: int