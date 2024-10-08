from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from ..api.views import (ChangePasswordAPIView, ConfirmEmailView, LogoutView,
                         RequestPasswordReset, ResetPassword, UserLoginAPIView,
                         UserRegistrationAPIView)


urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='create-user'),
    path('login/', UserLoginAPIView.as_view(), name='login-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),

    path('reset-password-request/', RequestPasswordReset.as_view(), name='password_reset_request'),
    path('reset/<str:uidb64>/<str:token>/', ResetPassword.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),

    path('account-confirm/<str:uidb64>/<str:token>/', ConfirmEmailView.as_view(), name='account-confirm'),
]
