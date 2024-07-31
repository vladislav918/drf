from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    ReadListModelViewSet,
    AuthorDetailView,
    RatingAPIView,
    CommentBookAPIView,
    BookDocumentView,
)

router = DefaultRouter()
router.register(r'book', BookViewSet, 'book')
router.register(r'read-book', ReadListModelViewSet, basename='read-book')
router.register(r'book-search', BookDocumentView, basename='book-search')
router.register(r'author', AuthorDetailView, basename='author')


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/book/<int:book_pk>/comments/', CommentBookAPIView.as_view(), name='comment-list'),
    path('api/v1/book/<int:book_pk>/ratings/', RatingAPIView.as_view(), name='rating'),
]
