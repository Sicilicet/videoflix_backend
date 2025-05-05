from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from content_app.models import Video
from watch_history_app.models import WatchHistory


class UpdateWatchHistory(APIView):
    serializer_class = None

    def post(self, request):
        """
        This function saves the watch history from a user. It creates or overwrites an existing database entry with the user, video ID and a timestamp.
        """

        user = request.user
        video_id = request.data.get("video_id")
        timestamp = request.data.get("timestamp")

        if not video_id or timestamp is None:
            return Response(
                {"error": "Video ID and timestamp are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            video = Video.objects.get(id=video_id)
            watch_history, created = WatchHistory.objects.get_or_create(
                user=user, video=video
            )
            watch_history.timestamp = timestamp
            watch_history.save()

            return Response(
                {"message": "Watch history updated"}, status=status.HTTP_200_OK
            )

        except Video.DoesNotExist:
            return Response(
                {"error": "Video does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return Response(
                {"message": "Something went wrong while updating the watch history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
