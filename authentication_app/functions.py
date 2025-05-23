from django.core.mail import send_mail
from django.template.loader import render_to_string
from videoflix import settings
from django.core.signing import TimestampSigner
from django.contrib.auth import get_user_model
import os

signer = TimestampSigner()
User = get_user_model()
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', default='http://localhost:4200')


def send_verification_email(request, user):
    """
    This function sends the verification email to the user. The HTML is created in the templates folder.
    """
    token = signer.sign(user.email)
    subject = "Confirm your email"
    verification_url = f"{FRONTEND_BASE_URL}/verification/{token}"
    html_message = render_to_string(
        "verification_email.html", {"user": user, "verification_url": verification_url}
    )
    recipient_list = [user.email]
    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
    )


def send_reset_password_email(request, email):
    """
    This function sends the reset password email to the user. The HTML is created in the templates folder.
    """
    token = signer.sign(email)
    subject = "Reset Videoflix password"
    reset_password_url = f"{FRONTEND_BASE_URL}/reset-password/{token}"
    html_message = render_to_string(
        "reset_password_email.html", {"reset_password_url": reset_password_url}
    )
    recipient_list = [email]
    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
    )
