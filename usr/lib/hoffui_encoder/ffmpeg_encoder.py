"""
FFMPEG Encoder Module
Handles all video encoding operations using FFMPEG.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from Functions import DEBUG


@dataclass
class VideoInfo:
    """Data class to hold video file information."""

    filename: str
    duration: float
    width: int
    height: int
    aspect_ratio: str
    video_codec: str
    audio_codec: str
    bitrate: int
    file_size: int
    fps: float


@dataclass
class EncodingSettings:
    """Data class to hold encoding settings."""

    # Video settings
    video_codec: str = "libx264"
    video_bitrate: str = "2000k"
    resolution: str = "Original"  # Original, 1920x1080, 1280x720, etc.
    fps: str = "Original"  # Original, 24, 30, 60
    crf: int = 23  # Constant Rate Factor (0-51, lower = better quality)
    preset: str = "medium"  # ultrafast, superfast, veryfast, etc.

    # Audio settings
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    audio_sample_rate: str = "Original"  # Original, 44100, 48000
    audio_channels: str = "Original"  # Original, 1 (mono), 2 (stereo)

    # Output settings
    output_format: str = "mp4"
    output_directory: str = ""


class FFMPEGEncoder:
    """Main FFMPEG encoding class."""

    SUPPORTED_VIDEO_FORMATS = [
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".3gp",
        ".mpg",
        ".mpeg",
        ".ts",
        ".vob",
        ".ogv",
    ]

    VIDEO_CODECS = {
        "H.264 (libx264)": "libx264",
        "H.265 (libx265)": "libx265",
        "VP9": "libvp9",
        "VP8": "libvpx",
        "AV1": "libaom-av1",
    }

    AUDIO_CODECS = {
        "AAC": "aac",
        "MP3": "libmp3lame",
        "Opus": "libopus",
        "Vorbis": "libvorbis",
        "AC3": "ac3",
    }

    PRESETS = [
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    ]

    RESOLUTIONS = {
        "Original": None,
        "4K (3840x2160)": "3840x2160",
        "1080p (1920x1080)": "1920x1080",
        "720p (1280x720)": "1280x720",
        "480p (854x480)": "854x480",
        "360p (640x360)": "640x360",
    }

    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            raise RuntimeError(
                "FFMPEG not found. Please install FFMPEG and add it to PATH."
            )

    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFMPEG executable in system PATH."""
        try:
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Check common locations
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/ffmpeg/bin/ffmpeg",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def get_video_info(self, file_path: str) -> Optional[VideoInfo]:
        """Extract video information using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                file_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)

            # Find video and audio streams
            video_stream = None
            audio_stream = None

            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video" and not video_stream:
                    video_stream = stream
                elif stream.get("codec_type") == "audio" and not audio_stream:
                    audio_stream = stream

            if not video_stream:
                return None

            # Extract video information
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            duration = float(data.get("format", {}).get("duration", 0))
            file_size = int(data.get("format", {}).get("size", 0))

            # Calculate aspect ratio
            if width and height:
                from math import gcd

                aspect_gcd = gcd(width, height)
                aspect_ratio = f"{width//aspect_gcd}:{height//aspect_gcd}"
            else:
                aspect_ratio = "Unknown"

            # Get frame rate
            fps_str = video_stream.get("r_frame_rate", "0/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 0
            else:
                fps = float(fps_str)

            # Get bitrate
            bitrate = int(data.get("format", {}).get("bit_rate", 0))

            return VideoInfo(
                filename=os.path.basename(file_path),
                duration=duration,
                width=width,
                height=height,
                aspect_ratio=aspect_ratio,
                video_codec=video_stream.get("codec_name", "Unknown"),
                audio_codec=(
                    audio_stream.get("codec_name", "Unknown")
                    if audio_stream
                    else "None"
                ),
                bitrate=bitrate,
                file_size=file_size,
                fps=fps,
            )

        except Exception as e:
            if DEBUG:
                print(f"Error getting video info: {e}")
            return None

    def find_video_files(self, directory: str, recursive: bool = True) -> List[str]:
        """Find all video files in directory."""
        video_files = []

        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(
                        file.lower().endswith(ext)
                        for ext in self.SUPPORTED_VIDEO_FORMATS
                    ):
                        video_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and any(
                    file.lower().endswith(ext) for ext in self.SUPPORTED_VIDEO_FORMATS
                ):
                    video_files.append(file_path)

        return sorted(video_files)

    def build_ffmpeg_command(
        self, input_path: str, output_path: str, settings: EncodingSettings
    ) -> List[str]:
        """Build FFMPEG command based on encoding settings."""
        cmd = [self.ffmpeg_path, "-i", input_path]

        # Video encoding settings
        cmd.extend(["-c:v", settings.video_codec])

        if settings.video_codec in ["libx264", "libx265"]:
            cmd.extend(["-crf", str(settings.crf)])
            cmd.extend(["-preset", settings.preset])

        if settings.video_bitrate != "Auto":
            cmd.extend(["-b:v", settings.video_bitrate])

        # Resolution
        if (
            settings.resolution != "Original"
            and settings.resolution in self.RESOLUTIONS
        ):
            resolution = self.RESOLUTIONS[settings.resolution]
            if resolution:
                cmd.extend(["-vf", f"scale={resolution}"])

        # Frame rate
        if settings.fps != "Original":
            cmd.extend(["-r", settings.fps])

        # Audio encoding settings
        cmd.extend(["-c:a", settings.audio_codec])

        if settings.audio_bitrate != "Auto":
            cmd.extend(["-b:a", settings.audio_bitrate])

        if settings.audio_sample_rate != "Original":
            cmd.extend(["-ar", settings.audio_sample_rate])

        if settings.audio_channels != "Original":
            if settings.audio_channels == "1":
                cmd.extend(["-ac", "1"])
            elif settings.audio_channels == "2":
                cmd.extend(["-ac", "2"])

        # Output settings
        cmd.extend(["-y"])  # Overwrite output file
        cmd.append(output_path)

        return cmd

    def encode_video(
        self,
        input_path: str,
        output_path: str,
        settings: EncodingSettings,
        progress_callback=None,
    ) -> bool:
        """Encode a single video file."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Build command
            cmd = self.build_ffmpeg_command(input_path, output_path, settings)

            if DEBUG:
                print(f"FFMPEG Command: {' '.join(cmd)}")

            # Get video duration for progress calculation
            video_info = self.get_video_info(input_path)
            total_duration = video_info.duration if video_info else 0

            # Start encoding process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
            )

            # Monitor progress
            while True:
                output = process.stderr.readline()
                if output == "" and process.poll() is not None:
                    break

                if output and progress_callback and total_duration > 0:
                    # Parse FFMPEG progress output
                    if "time=" in output:
                        try:
                            time_str = output.split("time=")[1].split()[0]
                            if ":" in time_str:
                                time_parts = time_str.split(":")
                                current_time = (
                                    float(time_parts[0]) * 3600
                                    + float(time_parts[1]) * 60
                                    + float(time_parts[2])
                                )
                                progress = min(
                                    (current_time / total_duration) * 100, 100
                                )
                                progress_callback(
                                    progress, f"Encoding... {progress:.1f}%"
                                )
                        except:
                            pass

            return process.returncode == 0

        except Exception as e:
            if DEBUG:
                print(f"Encoding error: {e}")
            return False

    def get_output_path(
        self,
        input_path: str,
        output_directory: str,
        settings: EncodingSettings,
        maintain_structure: bool = True,
    ) -> str:
        """Generate output path for encoded file."""
        input_file = Path(input_path)
        filename_without_ext = input_file.stem

        # Add encoding suffix
        output_filename = f"{filename_without_ext}_encoded.{settings.output_format}"

        if maintain_structure:
            # Maintain directory structure relative to the base input directory
            return os.path.join(output_directory, output_filename)
        else:
            # Flatten structure - all files in output directory
            return os.path.join(output_directory, output_filename)

    def format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}h {minutes}m {secs}s"

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in bytes to human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
