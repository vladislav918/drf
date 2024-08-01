from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_password_reset_email(email, reset_url):
        subject = 'Password Reset Request'
        message = f'Please follow this link to reset your password: {reset_url}'
        email_from = 'your-email@example.com'
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
