from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:

    @staticmethod
    def generate_token(user_model):
        token = default_token_generator.make_token(user_model)
        uid = urlsafe_base64_encode(force_bytes(user_model.id))
        return uid, token

    @staticmethod
    def decode_uid(uidb64: str) -> str:
        return force_str(urlsafe_base64_decode(uidb64))

    @staticmethod
    def validate_token(user, token: str) -> bool:
        return default_token_generator.check_token(user, token)
    
    @staticmethod
    def generate_token_for_user(user) -> dict:
        token = RefreshToken.for_user(user)
        return {
            'refresh': str(token),
            'access': str(token.access_token)
        }
