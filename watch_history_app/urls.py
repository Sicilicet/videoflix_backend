from django.urls import path
from .views import UpdateWatchHistory

urlpatterns = [
    path("update_watch_history/", UpdateWatchHistory.as_view(), name="update_watch_history"),
]