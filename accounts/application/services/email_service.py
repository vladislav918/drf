from django.core.mail import send_mail

from accounts.application.services.token_service import TokenService


class EmailService:

    @staticmethod
    def send_verification_email(user_model, domain):
        uid, token = TokenService.generate_token(user_model)
        subject = 'Confirm your account'
        message = f'Please confirm your account: http://{domain}/api/users/account-confirm/{uid}/{token}/'
        send_mail(subject, message, 'your-email@example.com', [user_model.email])

    @staticmethod
    def send_password_reset_email(user, domain):
        uid, token = TokenService.generate_token(user)
        subject = 'Password reset'
        message = f'Reset your password: http://{domain}/api/users/reset/{uid}/{token}/'
        send_mail(subject, message, 'your-email@example.com', [user.email])
