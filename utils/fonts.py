"""
Font Resolution and Typography Styling Utility for Video Generation.
Provides Google / ElevenLabs-style elegant typography formatting for FFmpeg drawtext filters.
"""

import os
from pathlib import Path
from typing import Optional, Tuple


SYSTEM_FONT_SEARCH_PATHS = [
    # Custom project fonts
    Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Montserrat-Bold.ttf",
    Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Roboto-Bold.ttf",
    Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Inter-Bold.ttf",
    # Linux / Docker Debian / Ubuntu
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/roboto/hinted/Roboto-Bold.ttf"),
    Path("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    # macOS
    Path("/Library/Fonts/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/Library/Fonts/Supplemental/Arial.ttf"),
    # Windows
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
]


def resolve_best_font_path() -> Tuple[str, str]:
    """
    Returns (ffmpeg_font_param, font_type) suitable for FFmpeg drawtext.
    e.g. ("fontfile='/path/to/font.ttf'", "file") or ("font='Arial'", "name")
    """
    for font_path in SYSTEM_FONT_SEARCH_PATHS:
        if font_path.exists():
            # Escape path for FFmpeg filter string
            escaped_path = str(font_path).replace("\\", "/").replace(":", "\\:")
            return f"fontfile='{escaped_path}'", "file"
    
    # Fallback to standard font family name
    return "font='DejaVu Sans'", "name"


def format_ffmpeg_drawtext(
    text: str,
    x: str = "(w-text_w)/2",
    y: str = "h-240",
    fontsize: int = 38,
    fontcolor: str = "white",
    boxcolor: str = "0x0a0c16@0.85",
    boxborderw: int = 16,
    borderw: int = 2,
    bordercolor: str = "0x00f0ff",
    enable_expr: str = "1"
) -> str:
    """
    Generates an elegant, high-contrast FFmpeg drawtext filter string in the style of Google / ElevenLabs ads.
    """
    font_param, _ = resolve_best_font_path()
    
    # Sanitize text for FFmpeg drawtext filter string
    clean_text = text.replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")
    
    drawtext_str = (
        f"drawtext=text='{clean_text}':{font_param}:"
        f"fontsize={fontsize}:fontcolor={fontcolor}:"
        f"box=1:boxcolor={boxcolor}:boxborderw={boxborderw}:"
        f"borderw={borderw}:bordercolor={bordercolor}:"
        f"x={x}:y={y}:enable='{enable_expr}'"
    )
    return drawtext_str
