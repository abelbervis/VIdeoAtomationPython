"""
Centralized Configuration for NASA Shorts Generator.
Loads environment variables and sets defaults for paths, video, audio, and APIs.
"""

import os
import random
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
TEMP_DIR = BASE_DIR / "temp"
AUDIO_DIR = TEMP_DIR / "audio"
SUBTITLES_DIR = TEMP_DIR / "subtitles"
OUTPUT_DIR = BASE_DIR / "output"

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
SYSTEM_PROMPT_FILE = clean_env("SYSTEM_PROMPT_FILE", "system_prompt.txt")
SYSTEM_PROMPT_PATH = BASE_DIR / SYSTEM_PROMPT_FILE

# Viral Hook Styles for TikTok & Shorts Retention
HOOK_STYLE = clean_env("HOOK_STYLE", "auto").lower()
HOOK_STYLES = {
    "auto": "Balanced selection of viral hooks",
    "paradox": "Visual contradiction or impossible physics (Lo que estás viendo desafía la física...)",
    "threat": "Cosmic danger, destructive energy, or terrifying scale (Si este monstruo estuviera a un año luz...)",
    "mystery": "Unexplained cosmic anomaly or sudden discovery (Los telescopios acaban de captar algo desconcertante...)",
    "secret": "Shattering common belief with uncomfortable truth (La ciencia creía que esto era imposible...)",
    "random": "Randomized selection across all viral archetypes"
}

# Multi-Topic Content Categories & Domains
DEFAULT_CATEGORY = clean_env("CATEGORY", "auto").lower()
CONTENT_CATEGORIES = {
    "auto": "Automatic intelligent domain detection based on topic keywords",
    "space": "Space & Astrophysics: cosmos, planets, black holes, NASA, deep space telescopes",
    "nature": "Extreme Nature & Abyss: deep ocean, extreme habitats, dangerous fauna, volcanoes, evolution",
    "tech": "Frontier Technology & AI: artificial intelligence, quantum computing, robotics, futuristic innovation",
    "history": "Ancient Mysteries & Archaeology: lost civilizations, monuments, archaeological secrets, historic events",
    "science": "Science Curiosities & Human Body: neuroscience, medicine, biology, optical illusions, physics trivia"
}

CATEGORY_KEYWORDS = {
    "space": [
        "espacio", "space", "tierra", "marte", "agujero", "nasa", "galaxia", "hubble", "webb",
        "universo", "planeta", "estrella", "jupiter", "luna", "saturno", "cosmos", "astronauta",
        "sol", "solar", "orbita", "meteorito", "asteroide", "cometa", "jwst", "supernova",
        "pulsar", "quasar", "nebulosa", "apod", "astronomia", "telescopio", "vía láctea", "milky way",
        "black hole", "galaxy", "universe", "planet", "star", "moon", "asteroid", "comet",
        "nebula", "astronaut", "orbit", "solar system", "astro", "venus", "mercurio", "urano", "neptuno",
        "pluton", "exoplaneta", "exoplanet", "andromeda", "andrómeda", "interestelar", "interstellar",
        "月球", "火星", "黑洞", "宇宙", "银河", "恒星", "行星", "地球", "太空", "太阳", "韦伯", "航天"
    ],
    "nature": [
        "oceano", "ocean", "mar", "marina", "marinas", "marino", "abisal", "abismo", "marianas",
        "fosa", "tiburón", "tiburon", "shark", "ballena", "whale", "animal", "animales", "criatura",
        "criaturas", "depredador", "predator", "selva", "jungla", "jungle", "volcan", "volcán",
        "volcano", "tsunami", "terremoto", "earthquake", "dinosaurio", "dinosaur", "insecto",
        "hongo", "parasito", "parásito", "planta", "especie", "evolucion", "evolución", "fauna",
        "bosque", "deep sea", "underwater", "nature", "wildlife", "marine", "creature", "reptil",
        "abyss", "pulpo", "calamar", "squid", "veneno", "venenoso", "anaconda", "leon", "león",
        "selva amazonica", "glaciar", "glacier", "coral", "arrecife", "biodiversidad"
    ],
    "tech": [
        "inteligencia artificial", "artificial intelligence", "ia", "ai", "robot", "robotica",
        "robótica", "robotics", "computacion", "computación", "cuantica", "cuántica", "quantum",
        "chip", "semiconductor", "algoritmo", "algorithm", "software", "ciber", "cyber", "hacker",
        "internet", "futuro", "futurista", "tecnologia", "tecnología", "technology", "nanotecnologia",
        "nanotecnología", "biotecnologia", "biotecnología", "neuralink", "automatizacion",
        "automatización", "transistor", "supercomputadora", "supercomputer", "dron", "drone",
        "automovil autonomo", "metaverso", "computadora", "ordenador", "redes neuronales"
    ],
    "history": [
        "historia", "history", "antiguo", "antigua", "ancient", "arqueologia", "arqueología",
        "archaeology", "piramide", "pirámide", "pyramid", "egipto", "egypt", "roma", "romano",
        "rome", "imperio", "empire", "civilizacion", "civilización", "civilization", "mayas",
        "aztecas", "incas", "momia", "mummy", "faraon", "faraón", "tumba", "tomb", "ruinas",
        "ruins", "atlantida", "atlántida", "atlantis", "tesoro", "treasure", "milenario",
        "siglo", "edad media", "medieval", "gladiador", "esparta", "vikingo", "vikingos",
        "templario", "castillo", "manuscrito", "arqueologico", "arqueológico", "prehistoria",
        "alejandria", "alejandría", "grecia", "griego", "griegos", "babilonia", "mesopotamia",
        "coliseo", "monumento", "antiguedad", "antigüedad", "filosofo", "filósofo"
    ],
    "science": [
        "cerebro", "brain", "mente", "mind", "neurona", "neuronas", "neuron", "neurons", "cuerpo", "humano", "human body", "genetica",
        "genética", "adn", "dna", "celula", "célula", "cell", "celulas", "células", "virus", "bacteria", "medicina",
        "medicine", "ojo", "optica", "óptica", "ilusion", "ilusión", "psicologia", "psicología",
        "quimica", "química", "chemistry", "fisica", "física", "physics", "atomo", "átomo",
        "atom", "curiosidad", "curiosidades", "enfermedad", "neurologia", "neurología", "neurociencia", "neuroscience",
        "inmune", "hormona", "sueno", "sueño", "memoria", "molecula", "molécula", "laboratorio", "biologia", "biología"
    ]
}


def detect_topic_category(topic: str, fallback: str = "space") -> str:
    """Intelligently detects the content category of a topic string."""
    if not topic or not topic.strip():
        return fallback

    text = topic.lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                # Longer keywords have higher weight
                scores[cat] += len(kw.split()) * 2

    # Find highest scoring category
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat

    return fallback

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
    if custom_voice and str(custom_voice).strip():
        return str(custom_voice).strip()

    code = (lang or DEFAULT_LANGUAGE or "es").lower().strip()

    # If user configured a default voice in .env or environment via TTS_VOICE
    env_voice = (DEFAULT_TTS_VOICE or "").strip()
    if env_voice:
        voice_lower = env_voice.lower()
        # 1. Voice explicitly matches requested language code (e.g. "es-MX-JorgeNeural" for "es")
        if voice_lower.startswith(f"{code}-"):
            return env_voice

        # 2. Voice without language prefix (e.g. OpenAI "alloy", "nova") or when target matches default language
        other_lang_prefixes = [f"{c}-" for c in SUPPORTED_LANGUAGES if c != code]
        has_other_lang = any(voice_lower.startswith(prefix) for prefix in other_lang_prefixes)
        if not has_other_lang and (code == DEFAULT_LANGUAGE or env_voice != "es-ES-AlvaroNeural"):
            return env_voice

    # Fallback to language-specific standard voice from SUPPORTED_LANGUAGES
    if code in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[code]["default_voice"]

    return env_voice or "es-ES-AlvaroNeural"

# Video Formats & Aspect Ratio Presets
VIDEO_FORMATS = {
    "vertical": {
        "name": "vertical",
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "9:16",
        "orientation": "portrait",
        "subtitle_margin_bottom": 540,
        "subtitle_font_size": 44,
        "description": "Vertical 9:16 (1080x1920) - YouTube Shorts, TikTok, Instagram Reels (Shorts Safe Zone)",
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
                    margin_v = max(100, int(h * 0.28))
                    font_size = max(24, int(h * 0.023))
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
VIDEO_BITRATE = clean_env("VIDEO_BITRATE", "12000k")
VIDEO_CRF = int(clean_env("VIDEO_CRF", "18"))
VIDEO_PRESET = clean_env("VIDEO_PRESET", "fast")

# Default Target Duration for Shorts (in seconds)
DEFAULT_DURATION = 35
MIN_SCENE_DURATION = 3.5

# Subtitle Styling
SUBTITLE_FONT = "Arial"
SUBTITLE_FONT_SIZE = int(clean_env("SUBTITLE_FONT_SIZE", str(_default_format_cfg["subtitle_font_size"])))
SUBTITLE_PRIMARY_COLOR = "&H00FFFFFF"  # Crisp White in ASS &HAABBGGRR
SUBTITLE_HIGHLIGHT_COLOR = clean_env("SUBTITLE_HIGHLIGHT_COLOR", "random")  # Default or random
SUBTITLE_OUTLINE_COLOR = "&H00000000"  # Black outline
SUBTITLE_OUTLINE_WIDTH = 4.0
SUBTITLE_MARGIN_BOTTOM = int(clean_env("SUBTITLE_MARGIN_BOTTOM", str(_default_format_cfg["subtitle_margin_bottom"])))
SUBTITLE_DYNAMIC = clean_env("SUBTITLE_DYNAMIC", "true").lower() in ("true", "1", "yes")

# Curated High-Contrast Highlight Colors for Shorts/TikTok (ASS &HAABBGGRR& format)
CURATED_SUBTITLE_COLORS: Dict[str, Tuple[str, str]] = {
    "yellow": ("&H0000FFFF&", "Gold Yellow"),
    "cyan": ("&H00FFFF00&", "Electric Cyan"),
    "green": ("&H0000FF00&", "Neon Lime"),
    "orange": ("&H00008CFF&", "Blaze Orange"),
    "pink": ("&H00FF00FF&", "Cosmic Magenta"),
    "amber": ("&H0000D7FF&", "Solar Amber"),
}


def resolve_highlight_color(color_spec: Optional[str] = None, force_random: bool = False) -> Tuple[str, str]:
    """
    Resolve ASS subtitle highlight color from preset name, custom hex, or random selection.
    Returns: (ass_color_code, color_display_name)
    """
    spec = (color_spec if color_spec is not None else SUBTITLE_HIGHLIGHT_COLOR).strip().lower()

    if force_random or spec in ("random", "rand", "any", "auto"):
        chosen_key = random.choice(list(CURATED_SUBTITLE_COLORS.keys()))
        code, name = CURATED_SUBTITLE_COLORS[chosen_key]
        return code, f"{name} (randomized)"

    if spec in CURATED_SUBTITLE_COLORS:
        return CURATED_SUBTITLE_COLORS[spec]

    raw = (color_spec if color_spec is not None else SUBTITLE_HIGHLIGHT_COLOR).strip()
    # Support standard web hex (#RRGGBB) converted to ASS (&H00BBGGRR&)
    if raw.startswith("#") and len(raw) == 7:
        try:
            r, g, b = raw[1:3], raw[3:5], raw[5:7]
            return f"&H00{b}{g}{r}&", f"Custom ({raw})"
        except Exception:
            pass

    if not raw.startswith("&H"):
        raw = f"&H{raw}"
    if not raw.endswith("&"):
        raw = f"{raw}&"
    return raw, "Custom ASS Hex"


# Dynamic Style Variation & Shuffling
RANDOM_STYLE = clean_env("RANDOM_STYLE", "false").lower() in ("true", "1", "yes")
SHUFFLE_MUSIC = clean_env("SHUFFLE_MUSIC", "true").lower() in ("true", "1", "yes")

# Visual Scene Transitions (FFmpeg xfade)
ENABLE_TRANSITIONS = clean_env("ENABLE_TRANSITIONS", "true").lower() in ("true", "1", "yes")
DEFAULT_TRANSITION = clean_env("TRANSITION_TYPE", "fade")
TRANSITION_DURATION = float(clean_env("TRANSITION_DURATION", "0.45"))
SUPPORTED_TRANSITIONS = [
    "fade",
    "dissolve",
    "wipeleft",
    "wiperight",
    "slideleft",
    "slideright",
    "smoothleft",
    "smoothright",
    "circleopen",
    "fadeblack",
    "hblur",
    "random",
    "none",
]

# Audio Sound Effects (SFX) & Background Music
SFX_DIR = ASSETS_DIR / "sfx"
ENABLE_SFX = clean_env("ENABLE_SFX", "true").lower() in ("true", "1", "yes")
SFX_VOLUME = float(clean_env("SFX_VOLUME", "0.35"))
MUSIC_VOLUME = float(clean_env("MUSIC_VOLUME", "0.22"))


