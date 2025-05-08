from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from authentication_app.models import CustomUser
from content_app.models import Video
from content_app.serializers import DashboardVideoSerializer, HeroVideoSerializer, VideoSerializer
from watch_history_app.models import WatchHistory
from freezegun import freeze_time
from unittest.mock import patch


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class DashboardViewTests(APITestCase):

    @freeze_time("2023-01-01 12:00:00")
    def setUp(self):
        self.user, created = CustomUser.objects.get_or_create(
            username="testuser", password="test1234"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.categories = ["drama", "action", "documentary"]

        self.videos = []
        for i in range(10):
            with freeze_time(f"2023-01-{i + 1:02d} 14:00:00"):
                video = Video.objects.create(
                    id=i + 1,
                    title=f"Test Video {i + 1}",
                    description=f"A test video description {i + 1}",
                    category=self.categories[i % len(self.categories)],
                    thumbnail=f"thumbnail.jpg",
                    teaser=f"teaser.mp4",
                    video_file=f"video.mp4",
                )
                self.videos.append(video)

        self.categorized_videos = {"drama": [], "action": [], "documentary": []}

        for i, video in enumerate(self.videos):
            category = self.categories[i % len(self.categories)]
            video.category = category
            serialized_video = DashboardVideoSerializer(video)
            self.categorized_videos[category].append(serialized_video.data)

        self.watch_history = WatchHistory.objects.create(
            user=self.user, video=self.videos[0], timestamp=0
        )

        self.latest_videos = [
            DashboardVideoSerializer(video).data for video in self.videos[4:][::-1]
        ]

        self.my_videos = [
            DashboardVideoSerializer(video).data for video in self.videos[:1]
        ]

    def test_get_dashboard_data(self):
        url = reverse("dashboard")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["latest_videos"], self.latest_videos)
        self.assertEqual(response.data["my_videos"], self.my_videos)
        self.assertCountEqual(response.data["categories"], self.categories)
        self.assertEqual(response.data["category_videos"], self.categorized_videos)

    @patch(
        "content_app.views.get_latest_videos",
        side_effect=Exception("Get latest videos failed"),
    )
    def test_get_latest_videos_fails(self, mock_get_videos):
        url = reverse("dashboard")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch(
        "content_app.views.get_my_videos",
        side_effect=Exception("Get latest videos failed"),
    )
    def test_get_my_videos_fails(self, mock_get_videos):
        url = reverse("dashboard")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch(
        "content_app.models.Video.objects.values_list",
        side_effect=Exception("Get categories failed"),
    )
    def test_get_categories_fails(self, mock_get_categories):
        url = reverse("dashboard")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch(
        "content_app.views.get_category_videos",
        side_effect=Exception("Get latest videos failed"),
    )
    def test_get_category_videos_fails(self, mock_get_videos):
        url = reverse("dashboard")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_invalid_token(self):
        self.token = "123456"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        url = reverse("dashboard")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class HeroViewTests(APITestCase):

    @freeze_time("2023-01-01 12:00:00")
    def setUp(self):
        self.user, created = CustomUser.objects.get_or_create(
            username="testuser", password="test1234"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.categories = ["drama", "action", "documentary"]

        self.videos = []
        for i in range(10):
            with freeze_time(f"2023-01-{i + 1:02d} 14:00:00"):
                video = Video.objects.create(
                    id=i + 1,
                    title=f"Test Video {i + 1}",
                    description=f"A test video description {i + 1}",
                    category=self.categories[i % len(self.categories)],
                    thumbnail=f"thumbnail.jpg",
                    teaser=f"teaser.mp4",
                    video_file=f"video.mp4",
                )
                self.videos.append(video)

        self.categorized_videos = {"drama": [], "action": [], "documentary": []}

        for i, video in enumerate(self.videos):
            category = self.categories[i % len(self.categories)]
            video.category = category
            serialized_video = HeroVideoSerializer(video)
            self.categorized_videos[category].append(serialized_video.data)

        self.latest_video = HeroVideoSerializer(self.videos[-1]).data

    def test_get_latest_hero_video(self):
        hero_id = -1
        url = reverse("hero")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.latest_video)

    def test_get_selected_hero_video(self):
        hero_id = 3
        url = reverse("hero")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 3)

    def test_video_not_existing(self):
        hero_id = 100
        url = reverse("hero")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_id(self):
        url = reverse("hero")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_token(self):
        self.token = "123456"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        hero_id = 1
        url = reverse("hero")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.post(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(
        "content_app.views.get_latest_video",
        side_effect=Exception("Get latest videos failed"),
    )
    def test_get_latest_video_fails(self, mock_get_video):
        hero_id = -1
        url = reverse("hero")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch(
        "content_app.views.get_selected_video",
        side_effect=Exception("Get latest videos failed"),
    )
    def test_get_selected_video_fails(self, mock_get_video):
        hero_id = 1
        url = reverse("hero")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class HeroViewTests(APITestCase):

    @freeze_time("2023-01-01 12:00:00")
    def setUp(self):
        self.user, created = CustomUser.objects.get_or_create(
            username="testuser", password="test1234"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.categories = ["drama", "action", "documentary"]

        self.videos = []
        for i in range(10):
            with freeze_time(f"2023-01-{i + 1:02d} 14:00:00"):
                video = Video.objects.create(
                    id=i + 1,
                    title=f"Test Video {i + 1}",
                    description=f"A test video description {i + 1}",
                    category=self.categories[i % len(self.categories)],
                    thumbnail=f"thumbnail.jpg",
                    teaser=f"teaser.mp4",
                    video_file=f"video.mp4",
                )
                self.videos.append(video)

        self.categorized_videos = {"drama": [], "action": [], "documentary": []}

        for i, video in enumerate(self.videos):
            category = self.categories[i % len(self.categories)]
            video.category = category
            serialized_video = VideoSerializer(video).data
            self.categorized_videos[category].append(serialized_video)

        self.video = VideoSerializer(self.videos[2]).data
        self.video["timestamp"] = 0

    def test_get_video(self):
        video_id = 3
        resolution = 360
        url = reverse("video")
        url_with_query = f"{url}?id={video_id}&resolution={resolution}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.video)

    def test_id_not_existing(self):
        video_id = 100
        resolution = 360
        url = reverse("video")
        url_with_query = f"{url}?id={video_id}&resolution={resolution}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_video_no_id(self):
        resolution = 360
        url = reverse("video")
        url_with_query = f"{url}?resolution={resolution}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_no_resolution(self):
        video_id = 1
        url = reverse("video")
        url_with_query = f"{url}?id={video_id}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resolution_not_existing(self):
        video_id = 100
        resolution = 1
        url = reverse("video")
        url_with_query = f"{url}?id={video_id}&resolution={resolution}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_token(self):
        self.token = "123456"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        hero_id = 1
        url = reverse("video")
        url_with_query = f"{url}?id={hero_id}"

        response = self.client.post(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(
        "content_app.views.get_video",
        side_effect=Exception("Get video failed"),
    )
    def test_get_selected_video_fails(self, mock_get_video):
        video_id = 3
        resolution = 360
        url = reverse("video")
        url_with_query = f"{url}?id={video_id}&resolution={resolution}"

        response = self.client.get(url_with_query, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
