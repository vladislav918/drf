from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BookViewSet, ReadListModelViewSet


router = DefaultRouter()
router.register(r'book', BookViewSet, 'book')
router.register(r'read-book', ReadListModelViewSet, 'read-book')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
