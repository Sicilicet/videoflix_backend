from rest_framework import serializers
from rest_framework.test import APITestCase
from django.core.signing import TimestampSigner
from authentication_app.models import CustomUser
from authentication_app.serializers import RegistrationSerializer, ResetPasswordSerializer, UserVerificationSerializer
from freezegun import freeze_time


class RegistrationSerializerTests(APITestCase):

    def setUp(self):
        self.user_data = {
            "username": "testuser@example.com",
            "email": "testuser@example.com",
            "password": "password123",
        }

    def test_contains_expected_fields(self):
        serializer = RegistrationSerializer(instance=self.user_data)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['email']))

    def test_create(self):
        serializer = RegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        created_user = serializer.create()

        self.assertEqual(created_user.username, self.user_data["username"])
        self.assertEqual(created_user.email, self.user_data["email"])
        self.assertTrue(created_user.check_password(self.user_data["password"]))
        self.assertFalse(created_user.is_active)

    def test_password_is_hashed(self):
        serializer = RegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        created_user = serializer.create()

        self.assertNotEqual(created_user.password, self.user_data["password"])
        self.assertTrue(created_user.check_password(self.user_data["password"]))

    def test_missing_required_fields(self):
        incomplete_data = {
            "email": "testuser@example.com",
        }
        serializer = RegistrationSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_validate_email(self):
        email_user2 = "existing@email.com"
        serializer = RegistrationSerializer()
        response = serializer.validate_email(self.user_data["username"])
        self.assertNotEqual(response, email_user2)

    def test_email_already_exists(self):
        CustomUser.objects.create_user(**self.user_data)
        serializer = RegistrationSerializer()

        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.validate_email(self.user_data["username"])

        self.assertEqual(str(cm.exception.detail[0]), "error")


class ResetPasswordTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
            is_active=False,
        )
        self.signer = TimestampSigner()
        self.valid_token = self.signer.sign(self.user.email)

    def test_valid_token(self):
        serializer = ResetPasswordSerializer(data={"token": self.valid_token})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["token"], self.valid_token)

    @freeze_time("2023-01-01 12:00:00")
    def test_expired_token(self):
        token = self.signer.sign(self.user.email)
        with self.assertRaises(serializers.ValidationError):
            serializer = ResetPasswordSerializer(data={"token": token})
            with freeze_time("2023-01-02 14:00:00"):
                serializer.is_valid(raise_exception=True)

    def test_bad_signature(self):
        serializer = ResetPasswordSerializer(data={"token": "invalidtoken"})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_non_existent_user(self):
        fake_token = self.signer.sign("nonexistent@example.com")
        serializer = ResetPasswordSerializer(data={"token": fake_token})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_save_password(self):
        new_password = "new_password"
        serializer = ResetPasswordSerializer(data={"token": self.valid_token})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        serializer.save(password=new_password)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))


class UserVerificationSerializerTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123",
            is_active=False,
        )
        self.signer = TimestampSigner()
        self.valid_token = self.signer.sign(self.user.email)

    def test_valid_token(self):
        serializer = UserVerificationSerializer(data={"token": self.valid_token})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["token"], self.valid_token)

    @freeze_time("2023-01-01 12:00:00")
    def test_expired_token(self):
        token = self.signer.sign(self.user.email)
        with self.assertRaises(serializers.ValidationError):
            serializer = UserVerificationSerializer(data={"token": token})
            with freeze_time("2023-01-01 14:00:00"):
                serializer.is_valid(raise_exception=True)

    def test_bad_signature(self):
        serializer = UserVerificationSerializer(data={"token": "invalidtoken"})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_non_existent_user(self):
        fake_token = self.signer.sign("nonexistent@example.com")
        serializer = UserVerificationSerializer(data={"token": fake_token})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_save_activates_user(self):
        serializer = UserVerificationSerializer(data={"token": self.valid_token})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        serializer.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
