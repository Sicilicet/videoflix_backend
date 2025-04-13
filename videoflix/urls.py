from django.views.generic.base import RedirectView
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from authentication_app.views import (CustomLoginView, ForgotPasswordView, LogoutView, RegistrationView,
                                      ResendVerificationEmailView, ResetPasswordView, VerificationView)
from content_app.views import DashboardView, HeroView, VideoView
from watch_history_app.views import UpdateWatchHistory

urlpatterns = (
    [
        path("", RedirectView.as_view(url="/admin/", permanent=True), name="index"),
        path('admin/', admin.site.urls),
        path("django-rq/", include("django_rq.urls")),
        path("registration/", RegistrationView.as_view(), name="registration"),
        path("verification/", VerificationView.as_view(), name="verification"),
        path("resend_verifiction/", ResendVerificationEmailView.as_view(), name="resend_verification"),
        path("forgot_password/", ForgotPasswordView.as_view(), name="forgot_password"),
        path("reset_password/", ResetPasswordView.as_view(), name="reset_password"),
        path("login/", CustomLoginView.as_view(), name="login"),
        path("logout/", LogoutView.as_view(), name="logout"),
        path("dashboard/", DashboardView.as_view(), name="dashboard"),
        path("hero/", HeroView.as_view(), name="hero"),
        path("video/", VideoView.as_view(), name="video"),
        path("update_watch_history/", UpdateWatchHistory.as_view(), name="update_watch_history",
             ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + debug_toolbar_urls()
)
