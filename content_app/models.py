import os
from datetime import date
from django.db import models
import logging

logger = logging.getLogger(__name__)


def video_upload_to(instance, filename):
    """
    This function removes all empty spaces and replaces them with underscores. Then it creates the new path.
    """
    title_path = instance.title.replace(" ", "_")
    upload_path = os.path.join("videos", title_path, filename)
    logger.debug(f"Video upload path: {upload_path}")
    return upload_path


def thumbnail_upload_to(instance, filename):
    """
    This function removes all empty spaces and replaces them with underscores. Then it creates the new path.
    """
    title_path = instance.title.replace(" ", "_")
    upload_path = os.path.join("thumbnails", title_path, filename)
    logger.debug(f"Video upload path: {upload_path}")
    return upload_path


class Video(models.Model):
    CATEGORY_CHOICES = [
        ("documentary", "Documentary"),
        ("drama", "Drama"),
        ("romance", "Romance"),
    ]
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=5000)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES[0][0])
    thumbnail = models.ImageField(upload_to=thumbnail_upload_to)
    teaser = models.FileField(upload_to=video_upload_to)
    video_file = models.FileField(upload_to=video_upload_to)
    hls_file_360 = models.FileField(max_length=255, blank=True, null=True)
    hls_file_480 = models.FileField(max_length=255, blank=True, null=True)
    hls_file_720 = models.FileField(max_length=255, blank=True, null=True)
    hls_file_1080 = models.FileField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
