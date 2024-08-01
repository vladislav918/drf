from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserRegisterationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password = serializers.RegexField(
        regex=r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[a-zA-Z\d@$!%*?&]{8,}$',
        write_only=True,
        error_messages={
            'invalid': ('Пароль должен быть длиной не менее 8 символов с хотя бы одной заглавной буквой и символом')}
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'confirm_password')


    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data


    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials')


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer): 
    new_password = serializers.RegexField(
        regex=r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[a-zA-Z\d@$!%*?&]{8,}$',
        write_only=True,
        error_messages={
            'invalid': ('Пароль должен быть длиной не менее 8 символов с хотя бы одной заглавной буквой и символом')}
    )
    confirmed_password = serializers.CharField(write_only=True, required=True)
