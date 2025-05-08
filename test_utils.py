from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


def create_mock_image(name="test_image.jpg", size=(100, 100), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    image_io = io.BytesIO()
    image.save(image_io, format="JPEG")
    image_io.seek(0)
    return SimpleUploadedFile(name, image_io.read(), content_type="image/jpeg")


def create_mock_video(name="test_video.mp4"):
    video_content = b"Mock video content"
    return SimpleUploadedFile(name, video_content, content_type="video/mp4")
