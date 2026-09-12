"""
File operations, media downloaders, path sanitizers, and validation utilities.
"""

import json
import os
import re
import shutil
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional


def sanitize_filename(name: str) -> str:
    """Convert a human topic string into a clean, safe filename."""
    name = name.lower().strip()
    # Replace Spanish accents and special chars
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n',
        '¿': '', '?': '', '¡': '', '!': '', ':': '', '"': '', "'": '',
        '/': '_', '\\': '_', '(': '', ')': '', '[': '', ']': ''
    }
    for orig, rep in replacements.items():
        name = name.replace(orig, rep)
    name = re.sub(r'[^a-z0-9_\-\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return name or "video_output"


def format_date_display(date_input: Optional[str], language: str = "es") -> Optional[str]:
    """
    Format raw date strings (e.g. '2024-04-08' or '2015-07-14T00:00:00Z')
    into a clean, concise, elegant format for mobile video overlays:
    - es: '8 Abr 2024' (or '2024' if only year)
    - en: 'Apr 8, 2024'
    - zh: '2024年4月8日'
    """
    if not date_input:
        return None
    raw = str(date_input).strip()
    if not raw or raw.lower() in ["none", "unknown", "reciente", "n/a", "null"]:
        return None

    # Extract YYYY-MM-DD pattern
    match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', raw)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        months_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        months_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        lang = (language or "es").lower()
        if lang.startswith("zh"):
            return f"{year}年{month}月{day}日"
        elif lang.startswith("en"):
            m_name = months_en[month - 1] if 1 <= month <= 12 else str(month)
            return f"{m_name} {day}, {year}"
        else:
            m_name = months_es[month - 1] if 1 <= month <= 12 else str(month)
            return f"{day} {m_name} {year}"

    # Year-only pattern e.g. '2024'
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', raw)
    if year_match:
        return year_match.group(1)

    return raw[:16]


def clean_visual_subject(title_input: Optional[str], fallback_topic: str = "", max_chars: int = 34) -> str:
    """
    Cleans and formats a visual media title or topic into a concise, elegant subject label
    for video display (e.g. 'Cometa Pons-Brooks', 'Corona Solar', 'Nebulosa de la Tarántula').
    Removes bureaucratic prefixes, camera/telescope IDs, date tags, disclaimers, and all emojis.
    """
    raw = (title_input or fallback_topic or "").strip()
    if not raw:
        return "Observación Espacial"

    # Remove any existing emoji characters
    t = re.sub(r'[\U00010000-\U0010ffff\u200d\u2600-\u26ff\u2700-\u27bf\ufe0f]', '', raw)
    t = t.replace('"', '').replace("'", '').replace("`", '').strip()

    # Remove agency and telescope prefixes
    t = re.sub(r'^(NASA[\'’]s|Hubble[\'’]s|ESA[\'’]s|Webb[\'’]s|JWST[\'’]s)\s+', '', t, flags=re.I)
    t = re.sub(r'^(Hubble|Webb|NASA|Chandra|Spitzer|SOHO|SDO|Curiosity|Perseverance)\s+(Observes|Captures|Views|Reveals|Inspects|Studies)\s+', '', t, flags=re.I)
    t = re.sub(r'^(A|An|The)\s+(Panoramic\s+|Close-up\s+|Detailed\s+|Incredible\s+)?(View|Look|Image|Perspective|Photo|Mosaic)\s+of\s+', '', t, flags=re.I)
    t = re.sub(r'^(Unwinding|Revealing|Exploring|Observing)\s+', '', t, flags=re.I)
    t = re.sub(r'^(A|An|The)\s+', '', t, flags=re.I)

    # Remove parentheticals and date stamps
    t = re.sub(r'\s*\([^)]*\)', '', t)
    t = re.sub(r'\s*-\s*(19|20)\d{2}.*$', '', t)
    t = re.sub(r'^[:\-\s,]+|[:\-\s,]+$', '', t).strip()

    # If title still starts with generic Scene fallback
    if re.match(r'^Scene\s*\d+', t, flags=re.I):
        t = fallback_topic or "Observación Espacial"

    # Clean fallback topic as well if it had emojis
    t = re.sub(r'[\U00010000-\U0010ffff\u200d\u2600-\u26ff\u2700-\u27bf\ufe0f]', '', t).strip()

    # Truncate nicely if still too long
    if len(t) > max_chars:
        words = t.split()
        shortened = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > max_chars:
                break
            shortened.append(w)
            cur_len += len(w) + 1
        t = " ".join(shortened) if shortened else t[:max_chars]

    return t.strip() or "Observación Espacial"



def save_json(data: Any, filepath: Path) -> None:
    """Save serializable data to a JSON file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Optional[Any]:
    """Load JSON from a file if it exists."""
    filepath = Path(filepath)
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def sanitize_url(url: str) -> str:
    """
    Sanitize a URL by percent-encoding spaces, control characters,
    and non-ASCII characters in path and query without double-encoding existing escapes.
    """
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    try:
        parts = urllib.parse.urlsplit(url)
        unquoted_path = urllib.parse.unquote(parts.path)
        path = urllib.parse.quote(unquoted_path, safe="/~:@!$&'()*+,;=")
        unquoted_query = urllib.parse.unquote(parts.query)
        query = urllib.parse.quote(unquoted_query, safe="=&?/~:@!$'()*+,;")
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))
    except Exception:
        return url.replace(" ", "%20")


def download_file(url: str, dest_path: Path, timeout: int = 30) -> bool:
    """
    Download a file from a URL to dest_path with progress and error safety.
    Works with standard urllib and handles SSL, redirects, and URL sanitization.
    """
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    clean_url = sanitize_url(url)

    try:
        req = urllib.request.Request(
            clean_url,
            headers={
                "User-Agent": "NASA-Shorts-Generator/1.0 (Science Education Tool; Mozilla/5.0)"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response, open(dest_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        
        # Verify non-empty file
        if dest_path.exists() and dest_path.stat().st_size > 0:
            return True
        return False
    except Exception as e:
        print(f"  ⚠️ Error downloading {clean_url}: {e}")
        if dest_path.exists():
            dest_path.unlink(missing_ok=True)
        return False


def get_media_duration(filepath: Path) -> float:
    """
    Get duration in seconds of an audio or video file using ffprobe.
    Returns estimated fallback if ffprobe is unavailable.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return 0.0

    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(filepath)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception:
        # Fallback approximation for MP3 if ffprobe fails (approx 128kbps)
        size_bytes = filepath.stat().st_size
        return max(1.0, size_bytes / 16000.0)


def check_ffmpeg() -> bool:
    """Verify that ffmpeg is installed and accessible."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def clean_temp_directory(temp_dir: Path) -> None:
    """Safely remove temporary render files."""
    temp_dir = Path(temp_dir)
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception:
                pass
