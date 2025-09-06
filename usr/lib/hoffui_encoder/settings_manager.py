"""
Settings Manager for HoffUI Encoder
Handles loading/saving user settings and environment variables
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from Functions import DEBUG


@dataclass
class AppSettings:
    """Application settings data structure."""

    # API and AI settings
    openai_api_key: str = ""
    ai_encoding_enabled: bool = False

    # Video settings (only saved if AI not enabled)
    video_codec: str = "H.264 (libx264)"
    video_bitrate: str = "2000k"
    resolution: str = "Original"
    fps: str = "Original"
    crf: int = 23
    preset: str = "medium"

    # Audio settings (only saved if AI not enabled)
    audio_codec: str = "AAC"
    audio_bitrate: str = "128k"
    audio_sample_rate: str = "Original"
    audio_channels: str = "Original"

    # Output settings
    output_format: str = "mp4"
    output_directory: str = ""
    maintain_structure: bool = True
    overwrite_files: bool = False

    # App preferences
    load_settings_on_startup: bool = True
    processing_mode: str = "single"


class SettingsManager:
    """Manages application settings and environment variables."""

    def __init__(self):
        self.settings = AppSettings()
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "settings.json"
        self.env_file = Path(__file__).parent.parent.parent / ".env"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _get_config_directory(self) -> Path:
        """Get the appropriate configuration directory for the OS."""
        if platform.system() == "Windows":
            # Use APPDATA on Windows
            appdata = os.getenv("APPDATA", os.path.expanduser("~/AppData/Roaming"))
            return Path(appdata) / "HoffUI_Encoder"
        else:
            # Use XDG config on Linux/Unix
            xdg_config = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            return Path(xdg_config) / "HoffUI_Encoder"

    def load_env_file(self) -> Dict[str, str]:
        """Load environment variables from .env file."""
        env_vars = {}

        try:
            if self.env_file.exists():
                with open(self.env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip()

                if DEBUG:
                    print(f"Loaded environment file: {self.env_file}")

        except Exception as e:
            if DEBUG:
                print(f"Error loading .env file: {e}")

        return env_vars

    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment file."""
        try:
            # Use dotenv to load the .env file
            if self.env_file.exists():
                load_dotenv(self.env_file)
                api_key = os.getenv("OPENAI_API_KEY", "").strip()

                # Remove quotes if present
                if api_key.startswith('"') and api_key.endswith('"'):
                    api_key = api_key[1:-1]
                elif api_key.startswith("'") and api_key.endswith("'"):
                    api_key = api_key[1:-1]

                if DEBUG:
                    print(f"Loaded API key from: {self.env_file}")

                return api_key if api_key else None

        except Exception as e:
            if DEBUG:
                print(f"Error loading API key: {e}")

        return None

    def save_settings(self, settings: AppSettings) -> bool:
        """Save settings to configuration file."""
        try:
            # Create a copy of settings to modify for saving
            save_data = asdict(settings)

            # If AI encoding is enabled, clear manual settings except API key and basic preferences
            if settings.ai_encoding_enabled:
                save_data.update(
                    {
                        "video_codec": "",
                        "video_bitrate": "",
                        "resolution": "",
                        "fps": "",
                        "crf": 23,  # Keep default
                        "preset": "",
                        "audio_codec": "",
                        "audio_bitrate": "",
                        "audio_sample_rate": "",
                        "audio_channels": "",
                    }
                )

            with open(self.config_file, "w") as f:
                json.dump(save_data, f, indent=2)

            if DEBUG:
                print(f"Settings saved to: {self.config_file}")

            return True

        except Exception as e:
            if DEBUG:
                print(f"Error saving settings: {e}")
            return False

    def load_settings(self) -> AppSettings:
        """Load settings from configuration file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    data = json.load(f)

                # Create settings object from loaded data
                settings = AppSettings()
                for key, value in data.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)

                if DEBUG:
                    print(f"Settings loaded from: {self.config_file}")

                return settings

        except Exception as e:
            if DEBUG:
                print(f"Error loading settings: {e}")

        # Return default settings if loading fails
        return AppSettings()

    def settings_exist(self) -> bool:
        """Check if settings file exists."""
        return self.config_file.exists()

    def get_auto_load_api_key(self) -> Optional[str]:
        """Get API key from env file if DEBUG is enabled."""
        if DEBUG:
            return self.get_openai_api_key()
        return None
