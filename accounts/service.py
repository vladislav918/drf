from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str


def generate_token(user):
    """
    Генерирует токен для пользователя.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token



class EmailService:
    @staticmethod
    def send_password_reset_email(user, domain, uid, token):
        subject = 'Password Reset Request'
        message = f'Please follow this link to reset your password: http://{domain}/api/users/reset/{uid}/{token}/'
        email_from = 'your-email@example.com'
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)


    @staticmethod
    def send_email_verification(user, domain, uid, token):
        subject = 'Confirm your account.'
        message = f"http://{domain}/api/users/account-confirm/{uid}/{token}/"
        recipient_list = [user.email]
        email_from = 'your-email@example.com'
        send_mail(subject, message, email_from, recipient_list)
