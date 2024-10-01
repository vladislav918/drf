from django.contrib.auth import get_user_model

from accounts.domain.exceptions import UserNotFoundException


class UserRepository:

    @staticmethod
    def create(email: str, username: str, password: str):
        user_model = get_user_model().objects.create_user(email=email, username=username, password=password)
        return user_model

    @staticmethod
    def get_user_by_id(user_id: int):
        try:
            user_model = get_user_model().objects.get(pk=user_id)
            return user_model
        except:
            raise UserNotFoundException()

    @staticmethod
    def get_user_by_email(email: str):
        try:
            user_model = get_user_model().objects.get(email=email)
            return user_model
        except:
            raise UserNotFoundException()

    @staticmethod
    def get_user_model_instance(user_id):
        try:
            user_model = get_user_model().objects.get(pk=user_id)
            return user_model
        except:
            raise UserNotFoundException()

    @staticmethod
    def save(user_model):
        user_model.save()
