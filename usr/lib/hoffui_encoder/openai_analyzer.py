"""
HoffUI FFMPEG Encoder - AI-Powered Video Analysis Module

This module provides intelligent video analysis capabilities using OpenAI's API to
determine optimal encoding settings. It combines technical video analysis with
AI-powered optimization to achieve maximum quality with minimal file size.

Author: Brad Heffernan
Email: brad.heffernan83@outlook.com
Project: HoffUI Encoder
License: GNU General Public License v3.0

Features:
- Technical video analysis using FFMPEG probe capabilities
- AI-powered encoding optimization via OpenAI GPT models
- Fallback rule-based analysis for offline operation
- Intelligent parameter selection based on content analysis
- Quality vs. file size optimization algorithms
- Support for various video formats and codecs
- Error handling and graceful degradation

Dependencies:
- ffmpeg_encoder: Video information and encoding settings structures
- subprocess: FFMPEG probe execution for technical analysis
- json: Response parsing and data serialization
- os: Environment variable management for API keys
"""

import json
import subprocess
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# from pathlib import Path
from openai import OpenAI
from ffmpeg_encoder import EncodingSettings, VideoInfo

MODEL_NAME = "gpt-4.1-nano-2025-04-14"


@dataclass
class VideoAnalysis:
    """Container for video analysis results."""

    complexity_score: float
    motion_level: str  # "low", "medium", "high"
    scene_changes: int
    has_grain: bool
    has_dark_scenes: bool
    has_fine_details: bool
    audio_complexity: str  # "simple", "moderate", "complex"
    recommended_crf: int
    recommended_preset: str
    recommended_bitrate: Optional[int] = None


class OpenAIVideoAnalyzer:
    """Analyzes videos using OpenAI to determine optimal encoding settings."""

    def __init__(self, api_key: str = None):
        """Initialize the analyzer with OpenAI API key."""
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = OpenAI(api_key=api_key)

    def set_api_key(self, api_key: str):
        """Set the OpenAI API key."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def analyze_video_technical(self, file_path: str, progress_callback=None) -> Dict:
        """Analyze video file using ffprobe to extract technical data."""
        print(f"DEBUG: Starting technical analysis of {file_path}")
        if progress_callback:
            progress_callback(10, "Extracting video metadata...")
        try:
            # Get detailed video information
            cmd_info = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                "-show_frames",
                "-select_streams",
                "v:0",
                "-read_intervals",
                "%+#50",
                file_path,
            ]

            result = subprocess.run(
                cmd_info, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {result.stderr}")

            data = json.loads(result.stdout)
            print(
                f"DEBUG: Successfully extracted technical data from {os.path.basename(file_path)}"
            )
            if progress_callback:
                progress_callback(30, "Analyzing video complexity...")

            # Analyze motion vectors and scene complexity
            cmd_motion = [
                "ffmpeg",
                "-i",
                file_path,
                "-vf",
                "select=between(n\\,0\\,100),showinfo",
                "-f",
                "null",
                "-",
                "-v",
                "info",
            ]

            motion_result = subprocess.run(  # noqa
                cmd_motion, capture_output=True, text=True
            )

            # Extract metrics from the output
            analysis = {
                "duration": float(data.get("format", {}).get("duration", 0)),
                "bitrate": int(data.get("format", {}).get("bit_rate", 0)),
                "width": 0,
                "height": 0,
                "fps": 0,
                "motion_level": "medium",
                "scene_complexity": "moderate",
            }

            # Extract video stream info
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    analysis["width"] = stream.get("width", 0)
                    analysis["height"] = stream.get("height", 0)
                    fps_str = stream.get("r_frame_rate", "0/1")
                    if "/" in fps_str:
                        num, den = fps_str.split("/")
                        analysis["fps"] = (
                            float(num) / float(den) if float(den) > 0 else 0
                        )
                    break

            return analysis

        except Exception as e:
            print(f"Technical analysis error: {e}")
            return {}

    def analyze_with_openai(
        self, technical_data: Dict, video_info: VideoInfo, progress_callback=None
    ) -> VideoAnalysis:
        """Use OpenAI to analyze video and recommend encoding settings."""

        # Calculate file size in MB from bytes
        file_size_mb = (
            video_info.file_size / (1024 * 1024) if video_info.file_size > 0 else 0
        )

        # Prepare the analysis prompt
        prompt = f"""
You are an expert video encoding analyst. Analyze this video and recommend optimal encoding settings for SIGNIFICANT file size reduction while maintaining good visual quality.

IMPORTANT: This video will be converted from {video_info.video_codec} to libx264 for better compatibility and smaller size.

Video Technical Data:
- Resolution: {technical_data.get('width', 0)}x{technical_data.get('height', 0)}
- Duration: {technical_data.get('duration', 0):.2f} seconds ({technical_data.get('duration', 0) / 60:.1f} minutes)
- Current Bitrate: {technical_data.get('bitrate', 0)} bps
- Frame Rate: {technical_data.get('fps', 0):.2f} fps
- File Size: {file_size_mb:.2f} MB ({file_size_mb / 1024:.2f} GB)

Video Properties:
- Current Codec: {video_info.video_codec}
- Audio Codec: {video_info.audio_codec}

OPTIMIZATION GOALS:
- Target 30-50% size reduction for files over 500MB
- Target 50-70% size reduction for files over 1GB
- Maintain visually acceptable quality
- Prioritize compatibility and streaming efficiency

Based on this data, provide recommendations in this exact JSON format:
{{
    "complexity_score": 0.7,
    "motion_level": "medium",
    "scene_changes": 150,
    "has_grain": false,
    "has_dark_scenes": false,
    "has_fine_details": true,
    "audio_complexity": "moderate",
    "recommended_crf": 25,
    "recommended_preset": "medium",
    "reasoning": "Your reasoning for these settings"
}}

ENCODING GUIDELINES:
- For large files (>500MB): Use CRF 24-28 for significant size reduction
- For x265 HEVC sources: Use CRF 25-28 (x264 needs higher CRF than x265)
- For long content (>30min): Favor smaller file sizes with CRF 26-28
- Audio complexity: "simple" for dialogue-heavy, "complex" for music/action
- PRESET OPTIMIZATION for multi-core systems:
  * Use "medium" preset for balanced speed/quality (recommended for most cases)
  * Use "fast" preset for high motion content or when speed is priority
  * Use "slow" preset only for very low motion content or when encoding time is not a concern
  * Avoid "slower" and "veryslow" presets unless encoding time is unlimited
- Consider motion level: high motion = faster preset, low motion = slower preset
- Multi-threading will significantly speed up encoding without quality loss
"""

        try:
            if not self.api_key or not self.client:
                # Fallback to rule-based analysis if no API key
                print("DEBUG: No OpenAI API key, using fallback analysis")
                if progress_callback:
                    progress_callback(60, "Using fallback analysis...")
                return self._fallback_analysis(technical_data, video_info)

            if progress_callback:
                progress_callback(50, "Sending video data to AI for analysis...")
            print(f"DEBUG: Sending request to OpenAI model {MODEL_NAME}")
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert video encoding analyst focused on optimizing quality vs file size.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.1,
            )

            if progress_callback:
                progress_callback(80, "Processing AI analysis results...")
            # Parse the response
            content = response.choices[0].message.content
            print(f"DEBUG: OpenAI Response: {content[:200]}...")  # Log first 200 chars

            # Extract JSON from the response
            import re

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                print(
                    f"DEBUG: Successfully parsed OpenAI analysis: CRF {analysis_data.get('recommended_crf', 23)}, Preset {analysis_data.get('recommended_preset', 'medium')}"
                )
                return VideoAnalysis(
                    complexity_score=analysis_data.get("complexity_score", 0.5),
                    motion_level=analysis_data.get("motion_level", "medium"),
                    scene_changes=analysis_data.get("scene_changes", 100),
                    has_grain=analysis_data.get("has_grain", False),
                    has_dark_scenes=analysis_data.get("has_dark_scenes", False),
                    has_fine_details=analysis_data.get("has_fine_details", True),
                    audio_complexity=analysis_data.get("audio_complexity", "moderate"),
                    recommended_crf=analysis_data.get("recommended_crf", 23),
                    recommended_preset=analysis_data.get(
                        "recommended_preset", "medium"
                    ),
                )
            else:
                print("No JSON found in OpenAI response, using fallback analysis")
                return self._fallback_analysis(technical_data, video_info)

        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            # Provide more specific error messages
            if "api_key" in str(e).lower():
                print("Error: Invalid or missing OpenAI API key")
            elif "model" in str(e).lower():
                print(f"Error: Model {MODEL_NAME} not available or accessible")
            elif "rate limit" in str(e).lower():
                print("Error: OpenAI API rate limit exceeded")
            else:
                print(f"Error: {str(e)}")

        # Fallback to rule-based analysis
        return self._fallback_analysis(technical_data, video_info)

    def _fallback_analysis(
        self, technical_data: Dict, video_info: VideoInfo
    ) -> VideoAnalysis:
        """Fallback rule-based analysis when OpenAI is not available."""

        # Calculate complexity based on resolution and bitrate
        width = technical_data.get("width", 1920)
        height = technical_data.get("height", 1080)
        bitrate = technical_data.get("bitrate", 5000000)
        fps = technical_data.get("fps", 30)
        duration = technical_data.get("duration", 0)
        file_size_mb = (
            video_info.file_size / (1024 * 1024) if video_info.file_size > 0 else 0
        )

        # Resolution complexity factor
        pixel_count = width * height
        if pixel_count > 3840 * 2160 * 0.8:  # 4K
            base_crf = 25  # More aggressive for 4K
            preset = "medium"  # Faster for large resolution
        elif pixel_count > 1920 * 1080 * 0.8:  # 1080p
            base_crf = 26  # More aggressive for 1080p
            preset = "medium"  # Balanced speed/quality
        else:  # Lower resolution
            base_crf = 27
            preset = "medium"

        # Adjust for large files (aggressive compression)
        if file_size_mb > 1000:  # Files over 1GB
            base_crf += 2  # Much more aggressive
            preset = "medium"  # Balance compression and speed for large files
        elif file_size_mb > 500:  # Files over 500MB
            base_crf += 1  # More aggressive
            preset = "medium"  # Better balance for medium files

        # Adjust for x265 HEVC sources (need more aggressive compression for x264)
        if (
            video_info.video_codec
            and "265" in video_info.video_codec
            or "hevc" in video_info.video_codec.lower()
        ):
            base_crf += 1  # x264 needs higher CRF than x265 for similar quality
            print(
                "DEBUG: Detected x265/HEVC source, increasing CRF for x264 conversion"
            )

        # Adjust for long content (favor file size over quality)
        if duration > 3600:  # Over 1 hour
            base_crf += 1
        elif duration > 1800:  # Over 30 minutes
            base_crf += 0.5

        # Motion level estimation based on FPS
        if fps > 50:
            motion_level = "high"
        elif fps > 30:
            motion_level = "medium"
        else:
            motion_level = "low"

        # Ensure CRF stays within reasonable bounds
        base_crf = max(18, min(28, int(base_crf)))

        # Calculate expected bitrate for complexity analysis
        expected_bitrate = pixel_count * fps * 0.1  # Rough estimate

        return VideoAnalysis(
            complexity_score=min(bitrate / expected_bitrate, 1.0),
            motion_level=motion_level,
            scene_changes=int(duration * 2),  # Estimate based on duration
            has_grain=bitrate > expected_bitrate * 1.8,
            has_dark_scenes=False,  # Cannot determine without analysis
            has_fine_details=bitrate > expected_bitrate * 1.3,
            audio_complexity="simple",  # Default to simple for better compression
            recommended_crf=base_crf,
            recommended_preset=preset,
        )

    def create_optimized_settings(
        self, analysis: VideoAnalysis, base_settings: EncodingSettings
    ) -> EncodingSettings:
        """Create optimized encoding settings based on analysis."""

        # Start with base settings
        optimized = EncodingSettings(
            video_codec=base_settings.video_codec,
            audio_codec=base_settings.audio_codec,
            output_format="mp4",  # MP4 for better compatibility and compression
            resolution=base_settings.resolution,
            video_bitrate="",  # Always use CRF mode for better quality/size ratio
            audio_bitrate=base_settings.audio_bitrate,
            crf=analysis.recommended_crf,
            preset=analysis.recommended_preset,
        )

        # Optimize audio settings based on complexity for file size
        if analysis.audio_complexity == "simple":
            optimized.audio_bitrate = "128k"  # Lower bitrate for simple audio
        elif analysis.audio_complexity == "complex":
            optimized.audio_bitrate = "192k"  # Moderate bitrate even for complex audio
        else:  # moderate
            optimized.audio_bitrate = "160k"  # Balanced bitrate (reduced from 192k)

        # Additional optimizations for file size reduction
        if analysis.complexity_score < 0.5:
            # Low complexity content can use higher CRF (smaller file)
            optimized.crf = min(28, analysis.recommended_crf + 2)
        elif analysis.has_fine_details and analysis.complexity_score > 0.8:
            # High detail content needs lower CRF (better quality)
            optimized.crf = max(18, analysis.recommended_crf - 1)

        return optimized

    def analyze_video(
        self, file_path: str, video_info: VideoInfo, progress_callback=None
    ) -> Tuple[VideoAnalysis, EncodingSettings]:
        """Complete video analysis and settings recommendation."""

        # Technical analysis
        technical_data = self.analyze_video_technical(file_path, progress_callback)

        # AI analysis
        analysis = self.analyze_with_openai(
            technical_data, video_info, progress_callback
        )

        if progress_callback:
            progress_callback(90, "Generating optimized settings...")

        # Create base settings for optimization
        base_settings = EncodingSettings(
            video_codec="libx264",
            audio_codec="aac",
            output_format="mp4",
            resolution="Original",  # Keep original
            video_bitrate="",  # Use CRF mode (empty for optimal quality/size balance)
            audio_bitrate="192k",
            crf=23,  # Will be overridden by AI analysis
            preset="medium",  # Will be overridden by AI analysis
        )

        # Generate optimized settings
        optimized_settings = self.create_optimized_settings(analysis, base_settings)

        if progress_callback:
            progress_callback(100, "AI analysis complete!")

        return analysis, optimized_settings
