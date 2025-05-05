from django.urls import path
from .views import DashboardView, HeroView, VideoView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("hero/", HeroView.as_view(), name="hero"),
    path("video/", VideoView.as_view(), name="video"),
]