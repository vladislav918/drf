from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    ReadListModelViewSet,
    AuthorDetailView,
    RatingViewSet,
    CommentBookViewSet,
    BookDocumentView,
)

router = DefaultRouter()
router.register(r'book', BookViewSet, 'book')
router.register(r'book-search', BookDocumentView, basename='book-search')
router.register(r'book/(?P<book_pk>\d+)/comments', CommentBookViewSet, basename='comment')
router.register(r'book/(?P<book_pk>\d+)/ratings', RatingViewSet, basename='rating')
router.register(r'read-book', ReadListModelViewSet, basename='read-book')
router.register(r'author', AuthorDetailView, basename='author')


urlpatterns = [
    path('api/v1/', include(router.urls)),
]
