from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    ReadListModelViewSet,
    AuthorDetailView,
    RatingViewSet,
    CommentBookViewSet,
)


router = DefaultRouter()
router.register(r'book', BookViewSet, 'book')
router.register(r'book/(?P<book_pk>\d+)/comments', CommentBookViewSet, basename='comment')
router.register(r'book/(?P<book_pk>\d+)/ratings', RatingViewSet, basename='rating')
router.register(r'read-book', ReadListModelViewSet, 'read-book')
router.register(r'author', AuthorDetailView, 'author')


urlpatterns = [
    path('api/v1/', include(router.urls)),
]
