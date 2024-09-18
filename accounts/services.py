from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model

from .exceptions import (
    InvalidTokenException,
    InvalidUIDException,
    UserNotFoundException,
    EmailAlreadyVerifiedException
)

from .models import PasswordReset, User
from .constants import EmailType


class EmailConfirmationService:

    @staticmethod
    def send_email_verification(user, domain):
        EmailService.send_email(user, domain, email_type=EmailType.VERIFICATION.value)

    @staticmethod
    def confirm_email(uidb64, token):
        uid = TokenService.decode_uid(uidb64)

        user = UserService.get_user_by_uid(uid)

        if user.is_verified:
            raise EmailAlreadyVerifiedException()

        if TokenService.validate_token(user, token):
            UserService.change_is_verified_on_user(user)


class UserService:

    @staticmethod
    def change_is_verified_on_user(user):
        user.is_verified = True
        user.save()

    @staticmethod
    def get_user_by_uid(uid: str) -> str:
        User = get_user_model()
        try:
            return User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise UserNotFoundException()


class EmailService:

    @staticmethod
    def send_email(user, domain, email_type):
        uid, token = TokenService.generate_token(user)

        try:
            if email_type == 'verification':
                EmailService._send_verification_email(user, domain, uid, token)
            elif email_type == 'password_reset':
                EmailService._send_password_reset_email(user, domain, uid, token)
                reset = PasswordReset(email=user.email, token=token)
                reset.save()
        except:
            raise ValueError(f'Неправильный email_type {email_type}')

    @staticmethod
    def _send_verification_email(user, domain, uid, token):
        subject = 'Подтвердите вашу учетную запись.'
        message = f'Перейдите по ссылке для подтверждения: http://{domain}/api/users/account-confirm/{uid}/{token}/'
        EmailService._send_email_to_user(subject, message, user)

    @staticmethod
    def _send_password_reset_email(user, domain, uid, token):
        subject = 'Запрос на сброс пароля'
        message = f'Перейдите по ссылке для сброса пароля: http://{domain}/api/users/reset/{uid}/{token}/'
        EmailService._send_email_to_user(subject, message, user)

    @staticmethod
    def _send_email_to_user(subject, message, user):
        email_from = 'your-email@example.com'
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)


class TokenService:

    @staticmethod
    def generate_token(user):
        """
        Генерирует токен для пользователя.
        """
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return uid, token

    @staticmethod
    def decode_uid(uidb64: str) -> str:
        try:
            return force_str(urlsafe_base64_decode(uidb64))
        except (TypeError, ValueError, OverflowError):
            raise InvalidUIDException()

    @staticmethod
    def validate_token(user, token: str) -> bool:
        if not default_token_generator.check_token(user, token):
            raise InvalidTokenException()

        return True


class PasswordResetService:

    @staticmethod
    def request_password_reset(email, domain):
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise UserNotFoundException()

        EmailService.send_email(user, domain, email_type=EmailType.PASSWORD_RESET.value)

        return user

    @staticmethod
    def reset_password(token, new_password):
        reset_obj = PasswordReset.objects.get(token=token)

        user = User.objects.filter(email=reset_obj.email).first()

        if not user:
            raise UserNotFoundException()

        user.set_password(new_password)
        user.save()

        reset_obj.delete()

        return user, None