from dataclasses import dataclass


@dataclass
class RegisterUserCommand:
    email: str
    username: str
    password: str


@dataclass
class ConfirmEmailCommand:
    uidb64: str
    token: str


@dataclass
class LoginUserCommand:
    email: str
    password: str


@dataclass
class LogoutUserCommand:
    refresh: str


@dataclass
class RequestPasswordResetCommand:
    email: str 


@dataclass
class ReserPasswordCommand:
    new_password: str
    uidb64: str
    token: str


@dataclass
class ChangePasswordCommand:
    email: str
    new_password: str
    old_password: str