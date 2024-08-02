from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserRegisterationSerializer,
    UserLoginSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)

from .models import User
from .models import PasswordReset
from .service import EmailService, generate_token


class UserRegisterationAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = UserRegisterationSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            uid, token = generate_token(user)

            reset = PasswordReset(email=user.email, token=token)
            reset.save()

            EmailService.send_email_verification(user, request.get_host(), uid, token)

            return Response({'message': 'Confirmation email sent.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if user.is_verified:
            serializer = UserSerializer(user)
            token = RefreshToken.for_user(user)
            data = serializer.data
            data['tokens'] = {'refresh': str(token), 'access': str(token.access_token)}
            return Response(data, status=status.HTTP_200_OK)
        return Response({'error': 'Email has not been confirmed'})


class LogoutView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordReset(GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email__iexact=email).first()

        if user:
            uid, token = generate_token(user)

            reset = PasswordReset(email=email, token=token)
            reset.save()

            EmailService.send_password_reset_email(user, request.get_host(), uid, token)

            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        return Response({'error': 'User with credentials not found'}, status=status.HTTP_404_NOT_FOUND)


class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    def post(self, request, token, uidb64):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_obj = PasswordReset.objects.filter(token=token).first()

        if not reset_obj:
            return Response({'error':'Invalid token'}, status=400)

        user = User.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(request.data['new_password'])
            user.save()

            reset_obj.delete()

            return Response({'success':'Password updated'})
        return Response({'error':'No user found'}, status=404)


class ChangePasswordAPIView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']

            user = User.objects.get(email=request.user.email)

            user.password = make_password(new_password)
            user.save()

            return Response({'success':'Password updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(GenericAPIView):
    permission_classes = []

    def get(self, request, uidb64, token, format=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()

            try:
                reset_obj = PasswordReset.objects.filter(token=token).first()
                reset_obj.delete()
            except:
                pass

            return Response({'status': 'Confirmed'}, status=status.HTTP_200_OK)

        return Response({'status': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)
