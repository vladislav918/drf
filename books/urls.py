from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BookViewSet, ReadListModelViewSet, AuthorDetailView


router = DefaultRouter()
router.register(r'book', BookViewSet, 'book')
router.register(r'read-book', ReadListModelViewSet, 'read-book')
router.register(r'author', AuthorDetailView, 'author')


urlpatterns = [
    path('api/v1/', include(router.urls)),
]
