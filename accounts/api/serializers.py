import re

from django.core.validators import MinLengthValidator

from rest_framework import serializers

from ..domain.models import User


class PasswordValidator:
    def __call__(self, value):
        MinLengthValidator(8)(value)
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы один специальный символ.")
        
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserRegisterationSerializer(UserSerializer):
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        validators=[PasswordValidator()]
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        validators=[PasswordValidator()]
    )
    confirmed_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirmed_password']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        validators=[PasswordValidator()]
    )
