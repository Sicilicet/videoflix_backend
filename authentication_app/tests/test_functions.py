from django.core import mail
from django.template.loader import render_to_string
from django.core.signing import TimestampSigner
from django.test import TestCase
from authentication_app.functions import send_reset_password_email, send_verification_email
from authentication_app.models import CustomUser
from unittest.mock import patch
import os

signer = TimestampSigner()
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', default='http://localhost:4200')


class ResetPasswordEmailTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123"
        )

    def test_email_is_sent(self):
        send_reset_password_email(request=None, email=self.user.email)
        self.assertEqual(len(mail.outbox), 1)

    @patch('authentication_app.functions.signer.sign', return_value='fixed_token')
    def test_email_contains_correct_content(self, mock_sign):
        send_reset_password_email(request=None, email=self.user.email)
        email = mail.outbox[0]

        self.assertEqual(email.subject, "Reset Videoflix password")
        self.assertEqual(email.to, [self.user.email])
        expected_url = f"{FRONTEND_BASE_URL}/reset-password/fixed_token"
        self.assertIn(expected_url, email.alternatives[0][0])

    @patch('authentication_app.functions.signer.sign', return_value='fixed_token')
    def test_email_uses_correct_template(self, mock_sign):
        expected_url = f"{FRONTEND_BASE_URL}/reset-password/fixed_token"
        expected_html = render_to_string(
            "reset_password_email.html", {"reset_password_url": expected_url}
        )

        send_reset_password_email(request=None, email=self.user.email)

        email_html_content = mail.outbox[0].alternatives[0][0]
        self.assertEqual(email_html_content, expected_html)


class SendVerificationEmailTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password123"
        )

    def test_email_is_sent(self):
        send_verification_email(request=None, user=self.user)
        self.assertEqual(len(mail.outbox), 1)

    @patch('authentication_app.functions.signer.sign', return_value='fixed_token')
    def test_email_contains_correct_content(self, mock_sign):
        send_verification_email(request=None, user=self.user)
        email = mail.outbox[0]

        self.assertEqual(email.subject, "Confirm your email")
        self.assertEqual(email.to, [self.user.email])
        expected_url = f"{FRONTEND_BASE_URL}/verification/fixed_token"
        self.assertIn(expected_url, email.alternatives[0][0])

    @patch('authentication_app.functions.signer.sign', return_value='fixed_token')
    def test_email_uses_correct_template(self, mock_sign):
        expected_url = f"{FRONTEND_BASE_URL}/verification/fixed_token"
        expected_html = render_to_string(
            "verification_email.html", {"user": self.user, "verification_url": expected_url}
        )

        send_verification_email(request=None, user=self.user)

        email_html_content = mail.outbox[0].alternatives[0][0]
        self.assertEqual(email_html_content, expected_html)
