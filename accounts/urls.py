from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegisterationAPIView, UserLoginAPIView, LogoutView


urlpatterns = [
    path('register/', UserRegisterationAPIView.as_view(), name='create-user'),
    path('login/', UserLoginAPIView.as_view(), name='login-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
]