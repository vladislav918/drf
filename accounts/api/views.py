from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from accounts.application.commands import (ChangePasswordCommand,
                                           ConfirmEmailCommand,
                                           LoginUserCommand, LogoutUserCommand,
                                           RegisterUserCommand,
                                           RequestPasswordResetCommand,
                                           ReserPasswordCommand)

from accounts.application.use_cases import (ChangePasswordUseCase,
                                            ConfirmEmailUseCase,
                                            LoginUserUseCase,
                                            LogoutUserUseCase,
                                            RegisterUserUseCase,
                                            RequestPasswordResetUseCase,
                                            ResetPasswordUseCase)

from .serializers import (ChangePasswordSerializer,
                          ResetPasswordRequestSerializer,
                          ResetPasswordSerializer, UserLoginSerializer,
                          UserRegisterationSerializer, UserSerializer)


class UserRegistrationAPIView(GenericAPIView):
    serializer_class = UserRegisterationSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            command = RegisterUserCommand(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
            )
            use_case = RegisterUserUseCase()
            use_case.execute(command, request.get_host())

            return Response(
                {'message': 'Confirmation email sent.'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(GenericAPIView):
    permission_classes = []

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            command = ConfirmEmailCommand(
                uidb64=uidb64,
                token=token,
            )
            use_case = ConfirmEmailUseCase()
            use_case.execute(command)

            return Response(
                {'message': 'Email confirmed'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            command = LoginUserCommand(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            use_case = LoginUserUseCase()
            result = use_case.execute(command)

            user_serializer = UserSerializer(result['user'])
            data = user_serializer.data
            data['tokens'] = result['tokens']

            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            command = LogoutUserCommand(
                refresh=request.data['refresh'],
            )
            use_case = LogoutUserUseCase()
            use_case.execute(command)

            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordReset(GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):

            command = RequestPasswordResetCommand(
                email=serializer.validated_data['email'],
            )

            use_case = RequestPasswordResetUseCase()
            use_case.execute(command, request.get_host())

            return Response(
                {'success': 'We have sent you a link to reset your password'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    def put(self, request, token, uidb64):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            command = ReserPasswordCommand(
                new_password=serializer.validated_data['new_password'],
                uidb64=uidb64,
                token=token,
            )

            use_case = ResetPasswordUseCase()
            use_case.execute(command)

            return Response(
                {'success': 'Password updated'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            command = ChangePasswordCommand(
                new_password=serializer.validated_data['new_password'],
                old_password=serializer.validated_data['old_password'],
                email=request.user,
            )

            use_case = ChangePasswordUseCase()
            use_case.execute(command)

            return Response(
                {'success': 'Password updated'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
