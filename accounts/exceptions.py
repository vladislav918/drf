from rest_framework.exceptions import APIException


class InvalidUIDException(APIException):
    """Исключение для некорректного UID."""
    status_code = 400
    default_detail = 'Invalid UID.'


class UserNotFoundException(APIException):
    """Исключение для случая, когда пользователь не найден."""
    status_code = 404
    default_detail = 'User not found.'


class InvalidTokenException(APIException):
    """Исключение для некорректного токена."""
    status_code = 400
    default_detail = 'Invalid token or token has expired.'


class EmailAlreadyVerifiedException(APIException):
    """Исключение проверки подтвержденного аккаунта"""
    status_code = 400
    default_detail = 'Email is already verified.'
