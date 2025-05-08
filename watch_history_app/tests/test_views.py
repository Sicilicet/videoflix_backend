from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from authentication_app.models import CustomUser
from content_app.models import Video
from test_utils import create_mock_image, create_mock_video
from watch_history_app.models import WatchHistory
from unittest.mock import patch


class UpdateWatchHistoryTests(APITestCase):

    def setUp(self):
        self.user, created = CustomUser.objects.get_or_create(
            username="test@user.com", email="test@user.com", password="test1234"
        )
        self.token = Token.objects.create(user=self.user)
        self.video = Video.objects.create(
            id=1,
            title="Test Video",
            description="A test video description",
            category="drama",
            thumbnail=create_mock_image(),
            teaser=create_mock_video(),
            video_file=create_mock_video(),
        )
        self.watch_history = WatchHistory.objects.create(
            user=self.user, video=self.video, timestamp=0
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_watch_history(self):
        WatchHistory.objects.filter(user=self.user, video=self.video).delete()
        watch_history_count = WatchHistory.objects.filter(
            user=self.user, video=self.video
        ).count()
        self.assertEqual(watch_history_count, 0)

        url = reverse("update_watch_history")
        body = {
            "video_id": 1,
            "timestamp": 1,
        }
        self.client.post(url, body, format="json")
        watch_history_count = WatchHistory.objects.filter(
            user=self.user, video=self.video
        ).count()
        self.assertEqual(watch_history_count, 1)

    def test_update_watch_history(self):
        url = reverse("update_watch_history")
        body = {
            "video_id": 1,
            "timestamp": 1,
        }
        response = self.client.post(url, body, format="json")
        self.watch_history.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.watch_history.timestamp, 1)

    def test_no_video_id(self):
        url = reverse("update_watch_history")
        body = {
            "timestamp": 1,
        }
        response = self.client.post(url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_timestamp(self):
        url = reverse("update_watch_history")
        body = {
            "video_id": 1,
        }
        response = self.client.post(url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_video_id(self):
        url = reverse("update_watch_history")
        body = {
            "video_id": 2,
            "timestamp": 1,
        }
        response = self.client.post(url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_watch_history_update(self):
        url = reverse("update_watch_history")
        body = {
            "video_id": 1,
            "timestamp": 10,
        }
        self.client.post(url, body, format="json")
        self.watch_history.refresh_from_db()

        watch_history_count = WatchHistory.objects.filter(
            user=self.user, video=self.video
        ).count()
        self.assertEqual(watch_history_count, 1)

    @patch.object(WatchHistory, "save", side_effect=Exception("Save failed"))
    def test_save_failed(self, mock_save):
        url = reverse("update_watch_history")
        body = {
            "video_id": 1,
            "timestamp": 1,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_user_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token ")
        url = reverse("update_watch_history")
        body = {
            "video_id": 1,
            "timestamp": 1,
        }
        response = self.client.post(url, body, format="json")
        self.watch_history.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
