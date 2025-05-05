from django.urls import path
from .views import (
    CustomLoginView, ForgotPasswordView, LogoutView, RegistrationView,
    ResendVerificationEmailView, ResetPasswordView, VerificationView
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("verification/", VerificationView.as_view(), name="verification"),
    path("resend_verification/", ResendVerificationEmailView.as_view(), name="resend_verification"),
    path("forgot_password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset_password/", ResetPasswordView.as_view(), name="reset_password"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]