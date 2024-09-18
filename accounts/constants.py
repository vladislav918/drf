from enum import Enum


class EmailType(Enum):
    VERIFICATION = 'verification'
    PASSWORD_RESET = 'password_reset'
