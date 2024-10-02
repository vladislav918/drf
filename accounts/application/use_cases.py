from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.domain.exceptions import (EmailAlreadyVerifiedException,
                                        EmailNotVerifiedException,
                                        InvalidTokenException,
                                        UserNotFoundException)
from accounts.infrastructure.repositories import UserRepository

from .commands import (ChangePasswordCommand, ConfirmEmailCommand,
                       LoginUserCommand, RegisterUserCommand)
from .services.email_service import EmailService
from .services.token_service import TokenService


class RegisterUserUseCase:

    def execute(self, command: RegisterUserCommand, domain: str):
        user_model = UserRepository.create(command.email, command.username, command.password)
        EmailService.send_verification_email(user_model, domain)


class ConfirmEmailUseCase:

    def execute(self, command: ConfirmEmailCommand):
        uid = TokenService.decode_uid(command.uidb64)
        user_model = UserRepository.get_user_model_instance(uid)

        if user_model.is_verified:
            raise EmailAlreadyVerifiedException()

        if not TokenService.validate_token(user_model, command.token):
            raise InvalidTokenException()

        user_model.is_verified = True
        UserRepository.save(user_model)

        return user_model


class LoginUserUseCase:

    def execute(self, command: LoginUserCommand) -> dict:
        user_model = self._authenticate_user(command)

        tokens = TokenService.generate_token_for_user(user_model)

        return {
            'user': user_model,
            'tokens': tokens
        }

    def _authenticate_user(self, command: LoginUserCommand):
        user_model = authenticate(email=command.email, password=command.password)

        if user_model is None:
            raise UserNotFoundException("User with provided credentials not found.")

        if not user_model.is_verified:
            raise EmailNotVerifiedException("Email not verified.")

        return user_model


class LogoutUserUseCase:

    def execute(self, command):
        token = RefreshToken(command.refresh)
        token.blacklist()


class RequestPasswordResetUseCase:

    def execute(self, command, domain):
        user_model = UserRepository.get_user_by_email(command.email)
        EmailService.send_password_reset_email(user_model, domain)


class ResetPasswordUseCase:

    def execute(self, command):
        uid = TokenService.decode_uid(command.uidb64)
        user_model = UserRepository.get_user_model_instance(uid)

        if not TokenService.validate_token(user_model, command.token):
            raise InvalidTokenException()

        user_model.set_password(command.new_password)
        user_model.save()


class ChangePasswordUseCase:

    def execute(self, command: ChangePasswordCommand):
        user_model = UserRepository.get_user_by_email(command.email)

        if not user_model.check_password(command.old_password):
            raise InvalidTokenException("Old password is incorrect")

        user_model.set_password(command.new_password)
        user_model.save()
