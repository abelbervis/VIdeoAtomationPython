"""
Centralized Configuration for NASA Shorts Generator.
Loads environment variables and sets defaults for paths, video, audio, and APIs.
"""

import os
import sys
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
AUDIO_DIR = BASE_DIR / "audio"
SUBTITLES_DIR = BASE_DIR / "subtitles"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# Ensure essential directories exist
for directory in [ASSETS_DIR, MUSIC_DIR, AUDIO_DIR, SUBTITLES_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def _load_env_file():
    """Load variables from .env if present (built-in or python-dotenv)."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return

    try:
        import dotenv
        dotenv.load_dotenv(dotenv_path=env_file)
    except ImportError:
        # Minimal built-in .env parser
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v


_load_env_file()

# API Keys and Services
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
NASA_IMAGE_API_BASE = "https://images-api.nasa.gov"

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PEXELS_API_BASE = "https://api.pexels.com"

MEDIA_PROVIDER = os.getenv("MEDIA_PROVIDER", "auto").lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "")

# TTS Settings
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge").lower()
TTS_API_KEY = os.getenv("TTS_API_KEY", "")
DEFAULT_TTS_VOICE = os.getenv("TTS_VOICE", "es-ES-AlvaroNeural")

# Video Standards (Vertical YouTube Shorts / Reels / TikTok)
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
VIDEO_BITRATE = "5000k"

# Default Target Duration for Shorts (in seconds)
DEFAULT_DURATION = 35
MIN_SCENE_DURATION = 3.5

# Subtitle Styling (for vertical video safe zones)
SUBTITLE_FONT = "Arial"
SUBTITLE_FONT_SIZE = 46
SUBTITLE_PRIMARY_COLOR = "&H00FFFF"  # Yellow in BGR hex: &H00BBGGRR or &H00FFFFFF for white
SUBTITLE_OUTLINE_COLOR = "&H000000"  # Black outline
SUBTITLE_OUTLINE_WIDTH = 3.5
SUBTITLE_MARGIN_BOTTOM = 280  # Safe zone: above TikTok/Shorts UI controls
