from rest_framework.test import APITestCase
from datetime import date
from content_app.serializers import DashboardVideoSerializer
from content_app.serializers import HeroVideoSerializer


class DashboardSerializerTests(APITestCase):

    def setUp(self):
        self.dashboard_data = {
            "created_at": date(2023, 1, 1),
            "category": "drama",
            "thumbnail": "thumbnail.img",
        }

    def test_contains_expected_fields(self):
        serializer = DashboardVideoSerializer(instance=self.dashboard_data)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(["created_at", "category", "thumbnail"]))


class HeroVideoSerializerTests(APITestCase):

    def setUp(self):
        self.hero_video_data = {
            "title": "Video title",
            "description": "Video description",
            "teaser": "teaser.mp4",
        }

    def test_contains_expected_fields(self):
        serializer = HeroVideoSerializer(instance=self.hero_video_data)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(["title", "description", "teaser"]))


class VideoSerializerTests(APITestCase):

    def setUp(self):
        self.video_data = {
            "title": "Video title",
            "hls_file": "video_file.m3u8",
            "timestamp": 0,
        }
