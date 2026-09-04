"""
Centralized Configuration for NASA Shorts Generator.
Loads environment variables and sets defaults for paths, video, audio, and APIs.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

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


def sanitize_env_value(v: str) -> str:
    """Sanitize environment variable value, removing inline comments and outer quotes."""
    if not v:
        return ""
    v = v.strip()
    # If wrapped in quotes, extract the quoted string
    if (v.startswith('"') and '"' in v[1:]) or (v.startswith("'") and "'" in v[1:]):
        quote_char = v[0]
        end_idx = v.find(quote_char, 1)
        if end_idx != -1:
            return v[1:end_idx].strip()
    # Otherwise strip inline comments preceded by whitespace
    for delimiter in (" #", "\t#"):
        if delimiter in v:
            v = v.split(delimiter, 1)[0]
    return v.strip().strip("'\"").strip()


def _load_env_file():
    """Load variables from .env if present (built-in or python-dotenv)."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return

    try:
        import dotenv
        dotenv.load_dotenv(dotenv_path=env_file)
    except ImportError:
        pass

    # Ensure all values from .env are properly sanitized (stripping inline comments and extra quotes)
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = sanitize_env_value(v)
            os.environ[k] = v


_load_env_file()

def clean_env(key: str, default: str = "") -> str:
    """Retrieve an environment variable and strip extraneous quotes, spaces, and inline comments."""
    val = os.getenv(key)
    if val is None:
        return default
    v = sanitize_env_value(str(val))
    return v if v else default


# API Keys and Services
NASA_API_KEY = clean_env("NASA_API_KEY", "DEMO_KEY")
NASA_IMAGE_API_BASE = "https://images-api.nasa.gov"

PEXELS_API_KEY = clean_env("PEXELS_API_KEY", "")
PEXELS_API_BASE = "https://api.pexels.com"

MEDIA_PROVIDER = clean_env("MEDIA_PROVIDER", "auto").lower()

GEMINI_API_KEY = clean_env("GEMINI_API_KEY", "")
OPENAI_API_KEY = clean_env("OPENAI_API_KEY", "")
GROQ_API_KEY = clean_env("GROQ_API_KEY", "")
GROQ_MODEL = clean_env("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_BASE = clean_env("GROQ_API_BASE", "https://api.groq.com/openai/v1")
LLM_PROVIDER = clean_env("LLM_PROVIDER", "auto").lower()
LLM_API_BASE_URL = clean_env("LLM_API_BASE_URL", "")

# TTS Settings
TTS_PROVIDER = clean_env("TTS_PROVIDER", "edge").lower()
TTS_API_KEY = clean_env("TTS_API_KEY", "")
DEFAULT_TTS_VOICE = clean_env("TTS_VOICE", "es-ES-AlvaroNeural")

# Language and Voice Mappings
DEFAULT_LANGUAGE = clean_env("DEFAULT_LANGUAGE", "es").lower()
SUPPORTED_LANGUAGES = {
    "es": {
        "name": "Spanish",
        "default_voice": "es-ES-AlvaroNeural",
        "subtitle_font": "Arial",
    },
    "en": {
        "name": "English",
        "default_voice": "en-US-ChristopherNeural",
        "subtitle_font": "Arial",
    },
    "zh": {
        "name": "Chinese (Simplified Mandarin)",
        "default_voice": "zh-CN-YunxiNeural",
        "subtitle_font": "WenQuanYi Zen Hei",
    },
}

def get_language_voice(lang: str, custom_voice: str = "") -> str:
    """Return appropriate TTS voice based on selected language and optional override."""
    if custom_voice and custom_voice.strip():
        return custom_voice.strip()
    code = (lang or "es").lower().strip()
    if code in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[code]["default_voice"]
    # Fallback to Spanish or custom default voice
    return DEFAULT_TTS_VOICE or "es-ES-AlvaroNeural"

# Video Formats & Aspect Ratio Presets
VIDEO_FORMATS = {
    "vertical": {
        "name": "vertical",
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "9:16",
        "orientation": "portrait",
        "subtitle_margin_bottom": 280,
        "subtitle_font_size": 46,
        "description": "Vertical 9:16 (1080x1920) - YouTube Shorts, TikTok, Instagram Reels",
    },
    "horizontal": {
        "name": "horizontal",
        "width": 1920,
        "height": 1080,
        "aspect_ratio": "16:9",
        "orientation": "landscape",
        "subtitle_margin_bottom": 80,
        "subtitle_font_size": 42,
        "description": "Horizontal 16:9 (1920x1080) - YouTube, standard video",
    },
    "square": {
        "name": "square",
        "width": 1080,
        "height": 1080,
        "aspect_ratio": "1:1",
        "orientation": "square",
        "subtitle_margin_bottom": 100,
        "subtitle_font_size": 42,
        "description": "Square 1:1 (1080x1080) - Instagram Post, LinkedIn, Facebook",
    },
}

FORMAT_ALIASES = {
    "vertical": "vertical",
    "vert": "vertical",
    "portrait": "vertical",
    "shorts": "vertical",
    "short": "vertical",
    "tiktok": "vertical",
    "reels": "vertical",
    "reel": "vertical",
    "9:16": "vertical",
    "9/16": "vertical",
    "horizontal": "horizontal",
    "horiz": "horizontal",
    "landscape": "horizontal",
    "youtube": "horizontal",
    "yt": "horizontal",
    "16:9": "horizontal",
    "16/9": "horizontal",
    "wide": "horizontal",
    "widescreen": "horizontal",
    "square": "square",
    "cuadrado": "square",
    "1:1": "square",
    "1/1": "square",
    "post": "square",
}


def resolve_video_format(fmt_input: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve video format configuration from name, alias, or custom dimensions.
    Examples:
      - 'vertical', 'portrait', '9:16' -> 1080x1920
      - 'horizontal', 'landscape', '16:9' -> 1920x1080
      - 'square', '1:1' -> 1080x1080
      - '1280x720', '3840x2160' -> custom resolution
    """
    val = (fmt_input or clean_env("VIDEO_FORMAT", "vertical")).lower().strip()

    # Check aliases
    alias = FORMAT_ALIASES.get(val)
    if alias and alias in VIDEO_FORMATS:
        return dict(VIDEO_FORMATS[alias])

    # Check custom resolution like WIDTHxHEIGHT
    if "x" in val:
        try:
            parts = val.split("x", 1)
            w = int(parts[0].strip())
            h = int(parts[1].strip())
            if w > 0 and h > 0:
                if w > h:
                    orientation = "landscape"
                    aspect = f"{w}:{h}"
                    margin_v = max(40, int(h * 0.08))
                    font_size = max(24, int(h * 0.038))
                elif h > w:
                    orientation = "portrait"
                    aspect = f"{w}:{h}"
                    margin_v = max(60, int(h * 0.15))
                    font_size = max(24, int(h * 0.024))
                else:
                    orientation = "square"
                    aspect = "1:1"
                    margin_v = max(50, int(h * 0.10))
                    font_size = max(24, int(h * 0.038))
                return {
                    "name": f"custom_{w}x{h}",
                    "width": w,
                    "height": h,
                    "aspect_ratio": aspect,
                    "orientation": orientation,
                    "subtitle_margin_bottom": margin_v,
                    "subtitle_font_size": font_size,
                    "description": f"Custom {aspect} ({w}x{h})",
                }
        except (ValueError, IndexError):
            pass

    return dict(VIDEO_FORMATS["vertical"])


# Video Standards (Configurable preset or custom dimensions)
DEFAULT_VIDEO_FORMAT = clean_env("VIDEO_FORMAT", "vertical")
_default_format_cfg = resolve_video_format(DEFAULT_VIDEO_FORMAT)

VIDEO_WIDTH = int(clean_env("VIDEO_WIDTH", str(_default_format_cfg["width"])))
VIDEO_HEIGHT = int(clean_env("VIDEO_HEIGHT", str(_default_format_cfg["height"])))
VIDEO_FPS = int(clean_env("VIDEO_FPS", "30"))
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
VIDEO_BITRATE = "5000k"

# Default Target Duration for Shorts (in seconds)
DEFAULT_DURATION = 35
MIN_SCENE_DURATION = 3.5

# Subtitle Styling
SUBTITLE_FONT = "Arial"
SUBTITLE_FONT_SIZE = int(clean_env("SUBTITLE_FONT_SIZE", str(_default_format_cfg["subtitle_font_size"])))
SUBTITLE_PRIMARY_COLOR = "&H00FFFF"  # Yellow in BGR hex: &H00BBGGRR or &H00FFFFFF for white
SUBTITLE_OUTLINE_COLOR = "&H000000"  # Black outline
SUBTITLE_OUTLINE_WIDTH = 3.5
SUBTITLE_MARGIN_BOTTOM = int(clean_env("SUBTITLE_MARGIN_BOTTOM", str(_default_format_cfg["subtitle_margin_bottom"])))

