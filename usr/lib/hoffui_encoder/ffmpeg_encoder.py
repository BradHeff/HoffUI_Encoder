"""
FFMPEG Encoder Module
Handles all video encoding operations using FFMPEG.
"""

import os
import subprocess
import json
from typing import List, Optional
from dataclasses import dataclass
from Functions import DEBUG, Path
from system_detector import SystemDetector, SystemSpecs, OptimalSettings


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

        # Initialize system detection and optimal settings
        self.system_detector = SystemDetector()
        self.system_specs: Optional[SystemSpecs] = None
        self.optimal_settings: Optional[OptimalSettings] = None
        self._system_detected = False

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

    def _ensure_system_detected(self):
        """Ensure system detection has been performed."""
        if not self._system_detected:
            print("🔍 Performing system detection for optimal encoding settings...")
            self.system_specs, self.optimal_settings = (
                self.system_detector.detect_and_optimize()
            )
            self._system_detected = True
            print("✅ System detection complete!")

    def get_system_info(
        self,
    ) -> tuple[Optional[SystemSpecs], Optional[OptimalSettings]]:
        """Get system specifications and optimal settings."""
        self._ensure_system_detected()
        return self.system_specs, self.optimal_settings

    def refresh_system_info(self):
        """Force refresh of system detection - useful before encoding starts."""
        print("🔍 Refreshing system detection for optimal encoding settings...")
        self._system_detected = False  # Force re-detection
        self._ensure_system_detected()
        return self.system_specs, self.optimal_settings

    def display_system_info(self):
        """Display detected system information."""
        self._ensure_system_detected()
        if not self.system_specs or not self.optimal_settings:
            print("❌ System detection failed")
            return

        print("\n" + "=" * 60)
        print("🖥️  SYSTEM DETECTION RESULTS")
        print("=" * 60)
        print(
            f"💻 CPU: {self.system_specs.cpu_cores_physical} physical cores, {self.system_specs.cpu_cores_logical} logical cores"
        )
        print(
            f"🧠 Memory: {self.system_specs.memory_total_gb:.1f}GB total, {self.system_specs.memory_available_gb:.1f}GB available"
        )

        if self.system_specs.gpu_info:
            print(f"🎮 GPU: {', '.join(self.system_specs.gpu_info)}")
        else:
            print("🎮 GPU: Software rendering only")

        if self.system_specs.hw_acceleration:
            print(
                f"🚀 Hardware Acceleration: {', '.join(self.system_specs.hw_acceleration)}"
            )
        else:
            print("🚀 Hardware Acceleration: Not available")

        print("\n⚡ OPTIMAL ENCODING SETTINGS:")
        print(f"🔧 Optimal Threads: {self.optimal_settings.optimal_threads}")
        print(f"🛡️  Conservative Threads: {self.optimal_settings.conservative_threads}")
        if self.optimal_settings.preferred_hwaccel:
            print(
                f"🎯 Hardware Acceleration: {self.optimal_settings.preferred_hwaccel}"
            )
        print(f"📊 Buffer Size: {self.optimal_settings.buffer_size}")
        print("=" * 60 + "\n")

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
                aspect_ratio = f"{width // aspect_gcd}:{height // aspect_gcd}"
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
        """Build FFMPEG command based on encoding settings with dynamic system optimization."""
        # Ensure system detection has been performed
        self._ensure_system_detected()

        cmd = [self.ffmpeg_path]

        # Add hardware acceleration if available (must be before input)
        if self.optimal_settings and self.optimal_settings.preferred_hwaccel:
            cmd.extend(["-hwaccel", self.optimal_settings.preferred_hwaccel])
            if DEBUG:
                print(
                    f"DEBUG: Using hardware acceleration: {self.optimal_settings.preferred_hwaccel}"
                )

        # Input file
        cmd.extend(["-i", input_path])

        # Use dynamically detected optimal threading
        optimal_threads = (
            self.optimal_settings.optimal_threads if self.optimal_settings else 8
        )
        cmd.extend(["-threads", str(optimal_threads)])

        cmd.extend(["-strict", "-2"])  # Enable experimental features if needed

        # Use dynamic buffer settings based on system capabilities
        analyze_duration = (
            self.optimal_settings.analyze_duration if self.optimal_settings else "100M"
        )
        probe_size = (
            self.optimal_settings.probe_size if self.optimal_settings else "100M"
        )
        mux_queue_size = (
            self.optimal_settings.mux_queue_size if self.optimal_settings else 2048
        )

        cmd.extend(["-analyzeduration", analyze_duration])
        cmd.extend(["-probesize", probe_size])
        cmd.extend(["-max_muxing_queue_size", str(mux_queue_size)])

        # Add speed optimization flags
        cmd.extend(["-fflags", "+fastseek+genpts"])
        cmd.extend(["-avoid_negative_ts", "make_zero"])

        # Video encoding settings
        cmd.extend(["-c:v", settings.video_codec])

        if settings.video_codec in ["libx264", "libx265"]:
            cmd.extend(["-crf", str(settings.crf)])
            cmd.extend(["-preset", settings.preset])

            # Add codec-specific threading optimizations for speed
            if settings.video_codec == "libx264":
                # x264 threading optimizations for speed without quality loss
                thread_count = optimal_threads
                cmd.extend(
                    [
                        "-x264opts",
                        f"threads={thread_count}:sliced-threads=1:no-scenecut",
                    ]
                )
            elif settings.video_codec == "libx265":
                # x265 threading optimizations
                cmd.extend(["-x265-params", f"pools={optimal_threads}:frame-threads=4"])

        # Only add bitrate if it's specified and not empty (CRF mode doesn't need bitrate)
        if (
            settings.video_bitrate
            and settings.video_bitrate != "Auto"
            and settings.video_bitrate.strip()
        ):
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

        # Only add audio bitrate if it's specified and not empty
        if (
            settings.audio_bitrate
            and settings.audio_bitrate != "Auto"
            and settings.audio_bitrate.strip()
        ):
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

    def encode_video(  # noqa
        self,
        input_path: str,
        output_path: str,
        settings: EncodingSettings,
        progress_callback=None,
        stop_flag_callback=None,
    ) -> bool:
        """Encode a single video file with fallback options for stability."""
        print(f"DEBUG: encode_video called with input_path={input_path}")
        print(f"DEBUG: encode_video called with output_path={output_path}")

        # Ensure system detection has been performed only once per encoder instance
        self._ensure_system_detected()

        # Try encoding with different stability levels
        for attempt in range(2):
            try:
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Build command (modify for fallback attempts)
                cmd = self.build_ffmpeg_command(input_path, output_path, settings)

                # On second attempt, use more conservative settings
                if attempt == 1:
                    print(
                        "DEBUG: First attempt failed, trying conservative settings..."
                    )
                    # Use dynamically detected conservative threading
                    conservative_threads = (
                        self.optimal_settings.conservative_threads
                        if self.optimal_settings
                        else 4
                    )

                    # Build a new conservative command from scratch
                    cmd = [self.ffmpeg_path, "-i", input_path]
                    cmd.extend(["-threads", str(conservative_threads)])
                    # Remove hardware acceleration for fallback
                    cmd.extend(["-strict", "-2"])

                    # Use basic buffer settings
                    cmd.extend(["-analyzeduration", "100M"])
                    cmd.extend(["-probesize", "100M"])
                    cmd.extend(["-max_muxing_queue_size", "1024"])

                    # Add speed optimization flags
                    cmd.extend(["-fflags", "+fastseek+genpts"])
                    cmd.extend(["-avoid_negative_ts", "make_zero"])

                    # Video encoding settings
                    cmd.extend(["-c:v", settings.video_codec])

                    if settings.video_codec in ["libx264", "libx265"]:
                        cmd.extend(["-crf", str(settings.crf)])
                        cmd.extend(["-preset", settings.preset])

                        # Conservative codec-specific options
                        if settings.video_codec == "libx264":
                            cmd.extend(
                                [
                                    "-x264opts",
                                    f"threads={conservative_threads}:no-scenecut",
                                ]
                            )
                        elif settings.video_codec == "libx265":
                            cmd.extend(
                                [
                                    "-x265-params",
                                    f"pools={conservative_threads}:frame-threads=2",
                                ]
                            )

                    # Audio settings
                    cmd.extend(["-c:a", settings.audio_codec])
                    if (
                        settings.audio_bitrate
                        and settings.audio_bitrate != "Auto"
                        and settings.audio_bitrate.strip()
                    ):
                        cmd.extend(["-b:a", settings.audio_bitrate])

                    # Resolution and FPS (if not original)
                    if (
                        settings.resolution != "Original"
                        and settings.resolution in self.RESOLUTIONS
                    ):
                        resolution = self.RESOLUTIONS[settings.resolution]
                        if resolution:
                            cmd.extend(["-vf", f"scale={resolution}"])

                    if settings.fps != "Original":
                        cmd.extend(["-r", settings.fps])

                    # Audio sample rate and channels
                    if settings.audio_sample_rate != "Original":
                        cmd.extend(["-ar", settings.audio_sample_rate])

                    if settings.audio_channels != "Original":
                        if settings.audio_channels == "1":
                            cmd.extend(["-ac", "1"])
                        elif settings.audio_channels == "2":
                            cmd.extend(["-ac", "2"])

                    cmd.extend(["-y"])  # Overwrite output file
                    cmd.append(output_path)

                print(f"DEBUG: FFMPEG Command (attempt {attempt + 1}): {' '.join(cmd)}")

                # Get video duration for progress calculation
                video_info = self.get_video_info(input_path)
                total_duration = video_info.duration if video_info else 0
                print(f"DEBUG: Video duration: {total_duration} seconds")

                # Start encoding process
                print(f"DEBUG: Starting FFmpeg process (attempt {attempt + 1})...")
                result = self._run_ffmpeg_process(
                    cmd, total_duration, progress_callback, stop_flag_callback
                )

                if result:
                    return True  # Success!
                elif attempt == 0:
                    print("DEBUG: First attempt failed, will try fallback...")
                    continue  # Try again with fallback
                else:
                    return False  # Both attempts failed

            except Exception as e:
                print(f"ERROR: Encoding error (attempt {attempt + 1}): {e}")
                if attempt == 1:  # Last attempt
                    import traceback

                    traceback.print_exc()
                    return False

        return False

    def _run_ffmpeg_process(
        self, cmd, total_duration, progress_callback, stop_flag_callback
    ):
        """Run the FFmpeg process and monitor progress."""
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )

        # Collect stderr for debugging
        stderr_lines = []

        # Monitor progress
        while True:
            # Check if stop was requested
            if stop_flag_callback and stop_flag_callback():
                process.terminate()
                return False

            output = process.stderr.readline()
            if output == "" and process.poll() is not None:
                break

            if output:
                stderr_lines.append(output.strip())

                if progress_callback and total_duration > 0:
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
                        except Exception as e:
                            print(f"Progress monitoring error: {e}")

        print("DEBUG: FFmpeg process completed")
        return_code = process.returncode
        print(f"DEBUG: FFmpeg return code: {return_code}")

        if return_code != 0:
            # Print last few lines of stderr for debugging
            print("DEBUG: FFmpeg stderr output:")
            for line in stderr_lines[-10:]:  # Show last 10 lines
                if line.strip():
                    print(f"  {line}")

            # Handle specific error codes
            if return_code == -11:
                print(
                    "ERROR: FFmpeg segmentation fault - possible memory/threading issue with HEVC input"
                )
            elif return_code == 1:
                print(
                    "ERROR: FFmpeg general error - check command syntax and input file"
                )
            elif return_code == 234:
                print(
                    "ERROR: FFmpeg parameter error - invalid command line arguments or unsupported codec combination"
                )
            else:
                print(f"ERROR: FFmpeg failed with return code {return_code}")

        return return_code == 0

    def get_output_path(
        self,
        input_path: str,
        output_directory: str,
        settings: EncodingSettings,
        maintain_structure: bool = True,
        original_base_path: str = None,
    ) -> str:
        """Generate output path for encoded file."""
        input_file = Path(input_path)
        filename_without_ext = input_file.stem

        # Keep original filename without any suffix
        output_filename = f"{filename_without_ext}.{settings.output_format}"

        if maintain_structure and original_base_path:
            # Maintain directory structure relative to the original base path
            input_path_obj = Path(input_path)
            base_path_obj = Path(original_base_path)

            # Get the name of the selected folder to include in output structure
            selected_folder_name = base_path_obj.name

            # Get relative path from base directory
            try:
                relative_path = input_path_obj.relative_to(base_path_obj)
                relative_dir = relative_path.parent

                # Create full output path maintaining structure with selected folder name
                if relative_dir == Path("."):  # File is in root of selected folder
                    output_dir = Path(output_directory) / selected_folder_name
                else:
                    output_dir = (
                        Path(output_directory) / selected_folder_name / relative_dir
                    )

                # Ensure output directory exists
                output_dir.mkdir(parents=True, exist_ok=True)

                return str(output_dir / output_filename)
            except ValueError:
                # If relative path calculation fails, fall back to simple structure
                pass

        # Simple structure - all files in output directory
        output_path = Path(output_directory) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return str(output_path)

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
