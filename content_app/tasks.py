import os
import shutil
import subprocess
from django.conf import settings
from django.db import transaction
from content_app.models import Video


def to_wsl_path(path):
    """
    This function change the path for wsl.
    """
    if ":" in path and "\\" in path:
        drive, rest = path.split(":", 1)
        rest = rest.strip("\\").replace("\\", "/")
        return f"/mnt/{drive.lower()}/{rest}"
    return path


def convert(video_id):
    """
    This function converts a video file into the desired HLS files. It is called as a signal so it can run in the background.
    """
    video_instance = Video.objects.get(id=video_id)
    source_path = to_wsl_path(video_instance.video_file.path)
    folder_path = video_instance.title.replace(" ", "_")
    base_name = os.path.splitext(os.path.basename(video_instance.video_file.name))[0]
    output_dir = create_output_directory(folder_path)

    resolutions = {
        "360p": ("hls_file_360", "640x360"),
        "480p": ("hls_file_480", "854x480"),
        "720p": ("hls_file_720", "1280x720"),
        "1080p": ("hls_file_1080", "1920x1080"),
    }

    with transaction.atomic():
        for suffix, (field_name, resolution) in resolutions.items():
            process_resolution(
                video_instance,
                source_path,
                base_name,
                output_dir,
                suffix,
                field_name,
                resolution,
            )

        video_instance.save()


def create_output_directory(sanitized_folder_path):
    """
    This function creates the output directory for the HLS files based on the name of the video file.
    """
    output_dir = os.path.join(settings.MEDIA_ROOT, "videos", sanitized_folder_path, "HLS_files")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def process_resolution(video_instance, source, base_name, output_dir, suffix, field_name, resolution):
    """
    This function starts the process of starts the creation of the the HLS files. In the end it deletes the helper mp4 file.
    """
    resolution_file = os.path.join(output_dir, f"{base_name}_{suffix}.mp4")
    convert_to_resolution(source, resolution_file, resolution)

    hls_prefix = os.path.join(output_dir, f"{base_name}_{suffix}")
    m3u8_path = convert_to_hls(resolution_file, hls_prefix)

    relative_path = os.path.relpath(m3u8_path, settings.MEDIA_ROOT)
    setattr(video_instance, field_name, relative_path)

    delete_mp4(resolution_file)


def convert_to_resolution(source, output_name, resolution):
    """
    This function uses the FFmpeg tool to convert a video file to a specified resolution.
    """
    cmd = [
        "ffmpeg",
        "-i", source,
        "-s", resolution,
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-strict", "-2",
        to_wsl_path(output_name),
    ]
    subprocess.run(cmd, check=True)


def convert_to_hls(source, output_name_prefix):
    """
    This function converts an input file to a specified HLS file.
    """
    m3u8_file = f"{output_name_prefix}.m3u8"
    segment_pattern = f"{output_name_prefix}_%03d.ts"
    cmd = [
        "ffmpeg",
        "-i", source,
        "-codec", "copy",
        "-start_number", "0",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-f", "hls",
        "-hls_segment_filename", to_wsl_path(segment_pattern),
        to_wsl_path(m3u8_file),
    ]
    subprocess.run(cmd, check=True)
    return m3u8_file


def delete_mp4(resolution_file):
    """
    This function deletes the mp4 file that is created for creating the HLS files.
    """
    if os.path.exists(resolution_file):
        os.remove(resolution_file)


def delete_video_folder(folder_path):
    """
    This function deletes the video folder if a user deletes a video in the admin panel.
    """
    full_path = os.path.join(settings.MEDIA_ROOT, folder_path)
    if os.path.exists(full_path):
        shutil.rmtree(full_path)


def delete_thumbnail_folder(folder_path):
    """
    This function deletes the thumbnail folder if a user deletes a video in the admin panel.
    """
    full_path = os.path.join(settings.MEDIA_ROOT, folder_path)
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
