from django.db import models
from authentication_app.models import CustomUser
from content_app.models import Video


class WatchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    timestamp = models.PositiveIntegerField(default=0)
    last_watched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} watched {self.video.title if self.video else 'Unknown Video'} up to {self.timestamp} seconds"
