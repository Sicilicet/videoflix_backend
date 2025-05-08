from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from authentication_app.models import CustomUser
from unittest.mock import patch
from django.core.signing import TimestampSigner
from freezegun import freeze_time
from authentication_app.serializers import ResetPasswordSerializer, UserVerificationSerializer


class ForgotPasswordTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
            is_active=False,
        )

    def test_forgot_password(self):
        url = reverse("forgot_password")
        data = {"email": self.user.email}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_user_with_email(self):
        url = reverse("forgot_password")
        data = {"email": "no_user@example.com"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
        )
        self.client = APIClient()

    def test_login(self):
        url = reverse("login")
        data = {
            "username": self.user.email,
            "password": "password123",
        }

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_authenticated)
        self.assertEqual(response.data.get("email"), self.user.email)
        self.assertTrue(response.data["token"])

    def test_wrong_password(self):
        url = reverse("login")
        data = {
            "username": self.user.email,
            "password": "wrong_password",
        }

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_not_existing(self):
        url = reverse("login")
        data = {
            "username": "not_existing@no_mail.com",
            "password": "password123",
        }

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password(self):
        url = reverse("login")
        data = {
            "username": self.user.email,
        }

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        url = reverse("login")
        data = {
            "password": "password123",
        }

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(
        "rest_framework.authtoken.models.Token.objects.get_or_create",
        side_effect=Exception("Token creation failed"),
    )
    def test_token_creation_fails(self, mock_create):
        url = reverse("login")
        data = {
            "username": self.user.email,
            "password": "password123",
        }

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user, created = CustomUser.objects.get_or_create(
            username="testuser", password="test1234"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_logout(self):
        url = reverse("logout")

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_token(self):
        self.client.credentials()

        url = reverse("logout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token(self):
        self.token = '123456'
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        url = reverse("logout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(
        "rest_framework.authtoken.models.Token.delete",
        side_effect=Exception("Token deletion failed"),
    )
    def test_delete_token_fails(self, mock_delete):
        url = reverse("logout")

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegistrationTests(APITestCase):

    def test_register_user(self):
        url = reverse("registration")
        data = {
            "password": "password123",
            "email": "testuser@example.com",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_no_email(self):
        url = reverse("registration")
        data = {
            "password": "password123",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_register_no_password(self):
        url = reverse("registration")
        data = {
            "email": "testuser@example.com",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        url = reverse("registration")
        data = {"password": "password123", "email": "this_is_no_email"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_already_exists(self):
        url = reverse("registration")
        data = {"password": "password123", "email": "testuser@example.com"}
        CustomUser.objects.get_or_create(
            username="testuser@example.com", password="test1234"
        )

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
            is_active=False,
        )

    def test_resend_verification_email(self):
        url = reverse("resend_verification")
        data = {"email": self.user.email}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_user_with_email(self):
        url = reverse("resend_verification")
        data = {"email": "no_user@example.com"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(
        "authentication_app.views.send_verification_email",
        side_effect=Exception("Email send error"),
    )
    def test_send_email_fails(self, mocked_mail):
        url = reverse("resend_verification")
        data = {"email": self.user.email}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetPasswordTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
            is_active=False,
        )
        self.signer = TimestampSigner()

    def test_reset_password(self):
        url = reverse("reset_password")
        token = self.signer.sign(self.user.email)
        new_password = "new_password"
        data = {"token": token, "password": new_password}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(new_password))

    def test_no_token(self):
        url = reverse("reset_password")
        data = {"password": "new_password"}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password(self):
        url = reverse("reset_password")
        token = self.signer.sign(self.user.email)
        data = {"token": token}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        url = reverse("reset_password")
        data = {"token": "testuser@example.com123456", "password": "new_password"}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time("2023-01-01 12:00:00")
    def test_expired_token(self):
        token = self.signer.sign(self.user.email)

        with freeze_time("2023-01-02 14:01:00"):
            url = reverse("reset_password")
            data = {"token": token, "password": "new_password"}

            response = self.client.post(url, data, format="json")
            self.user.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(ResetPasswordSerializer, "save", side_effect=Exception("Save failed"))
    def test_save_failed(self, mock_save):
        url = reverse("reset_password")
        token = self.signer.sign(self.user.email)
        data = {"token": token, "password": "new_password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificationTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
            is_active=False,
        )
        self.signer = TimestampSigner()

    def test_verficate_user(self):
        url = reverse("verification")
        token = self.signer.sign(self.user.email)
        data = {"token": token}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)

    def test_no_token(self):
        url = reverse("verification")
        data = {}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        url = reverse("verification")
        data = {"token": "testuser@example.com123456"}

        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time("2023-01-01 12:00:00")
    def test_expired_token(self):
        token = self.signer.sign(self.user.email)

        with freeze_time("2023-01-01 14:01:00"):
            url = reverse("verification")
            data = {"token": token}

            response = self.client.post(url, data, format="json")
            self.user.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(
        UserVerificationSerializer, "save", side_effect=Exception("Save failed")
    )
    def test_save_failed(self, mock_save):
        url = reverse("verification")
        token = self.signer.sign(self.user.email)
        data = {"token": token}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
