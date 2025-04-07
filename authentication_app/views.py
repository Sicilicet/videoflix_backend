from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from authentication_app.functions import (
    send_reset_password_email,
    send_verification_email,
)
from authentication_app.serializers import (
    RegistrationSerializer,
    ResetPasswordSerializer,
    UserVerificationSerializer,
)
from django.contrib.auth import get_user_model
import traceback

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Creates a new user if the serializer is valid and sends a verification email.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.create()
                send_verification_email(request, user)
                return Response(status=status.HTTP_201_CREATED)
            except Exception as e:
                print("Email sending error:", str(e))
                traceback.print_exc()
                return Response(
                    {
                        "message": "An error occurred during user creation or email sending."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        This function saves the verification of the user if the serializer is valid.
        """
        serializer = UserVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"message": "User successfully verified."},
                    status=status.HTTP_200_OK,
                )
            except:
                return Response(
                    {"message": "An error occurred during user verification."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        This function resends the verification email.
        """
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            send_verification_email(request, user)
            return Response(
                {
                    "message": "If this email exists, a verification email has been sent."
                },
                status=status.HTTP_200_OK,
            )

        except:
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        This function sends the reset password email to the user.
        """
        email = request.data.get("email")

        try:
            User.objects.get(email=email)
            send_reset_password_email(request, email)
            return Response({"message": "Email sent."}, status=status.HTTP_200_OK)
        except:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        This function saves the reset the password if the serializer is valid.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                password = request.data.get("password")
                if password:
                    serializer.save(password=password)
                    return Response(
                        {"message": "Password successfully reset."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response(
                    {"message": "An error occurred during password reset."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        This function logs the user in if the serializer is vaild. Therefore the email and password are checked. If success the user email and token are returned.
        """
        serializer = self.serializer_class(data=request.data)

        data = {}
        if serializer.is_valid():
            try:
                user = serializer.validated_data["user"]
                Token.objects.filter(user=user).delete()
                token, created = Token.objects.get_or_create(user=user)
                data = {
                    "email": user.email,
                    "token": token.key,
                }
                return Response(data, status=status.HTTP_200_OK)

            except:
                return Response(
                    {"message": "An error occurred during Login."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        """
        This function logs out the user by deleting the token.
        """
        try:
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
