from content_app.models import Video
from content_app.serializers import (
    DashboardVideoSerializer,
    HeroVideoSerializer,
    VideoSerializer,
)
from watch_history_app.models import WatchHistory


def get_latest_videos():
    """
    This function gets the 6 latest videos and serializes them.
    """
    latest_videos = Video.objects.order_by("-created_at")[:6]
    latest_videos_serialized = DashboardVideoSerializer(latest_videos, many=True).data
    return latest_videos_serialized


def get_my_videos(request):
    """
    This function gets the videos the user has partly watched and serializes them.
    """
    watch_history = WatchHistory.objects.filter(user=request.user).select_related(
        "video"
    )
    video_ids = watch_history.values_list("video__id", flat=True)
    my_videos = Video.objects.filter(id__in=video_ids)
    my_videos_serialized = DashboardVideoSerializer(my_videos, many=True).data
    return my_videos_serialized


def get_category_videos(categories):
    """
    This function goes through the videos and returns all categories.
    """
    category_videos = {}
    for category in categories:
        videos = Video.objects.filter(category=category)
        category_videos[category] = DashboardVideoSerializer(videos, many=True).data
    return category_videos


def get_latest_video():
    """
    This function gets the newest video on the database and serializes it.
    """
    latest_video = Video.objects.order_by("created_at").last()
    video = latest_video
    serializer = HeroVideoSerializer(video)
    return serializer.data


def get_selected_video(video_id):
    """
    This function gets the video for the her section and serializes it.
    """
    video = Video.objects.get(id=video_id)
    serializer = HeroVideoSerializer(video)
    return serializer.data


def get_video(video_id, user, resolution):
    """
    This function gets the video the user picks and serializes it.
    """
    video = Video.objects.get(id=video_id)
    serializer = VideoSerializer(
        video, context={"user": user, "resolution": resolution}
    )
    return serializer.data


def get_user_timestamp(user, video_id):
    """
    Fetches the watch history timestamp for a specific user and video.
    """
    try:
        watch_history = WatchHistory.objects.get(user=user, video_id=video_id)
        return watch_history.timestamp
    except WatchHistory.DoesNotExist:
        return 0
