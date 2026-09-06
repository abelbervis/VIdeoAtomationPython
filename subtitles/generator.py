"""
Subtitle Generator for Vertical Shorts.
Generates synchronized .srt and styled .ass subtitles formatted for mobile vertical video.
Optimized for readability: short word chunks, high contrast colors, and mobile UI safe-zones.
"""

import math
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import (
    ASSETS_DIR,
    SUBTITLES_DIR,
    SUBTITLE_FONT,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_PRIMARY_COLOR,
    SUBTITLE_HIGHLIGHT_COLOR,
    SUBTITLE_OUTLINE_COLOR,
    SUBTITLE_OUTLINE_WIDTH,
    SUBTITLE_MARGIN_BOTTOM,
    SUBTITLE_DYNAMIC,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    SUPPORTED_LANGUAGES,
)


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds into SRT timestamp (HH:MM:SS,mmm)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def format_timestamp_ass(seconds: float) -> str:
    """Format seconds into ASS timestamp (H:MM:SS.cc)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


def is_cjk(text: str) -> bool:
    """Check if text contains Chinese or CJK characters."""
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def resolve_chinese_font(custom_font: Optional[str] = None) -> str:
    """
    Find the best font family name for Chinese text rendering in libass on Linux/Docker.
    Checks user override, fontconfig (fc-list), system font paths, and bundled assets.

    Guarantees returning a single clean font family name without commas,
    preventing corruption of the comma-delimited ASS Style line.
    """
    if custom_font and custom_font.strip():
        clean_name = custom_font.strip().split(",")[0].strip()
        if clean_name:
            print(f"  🔤 Subtitle font (custom override): {clean_name}")
            return clean_name

    # 1. Check fontconfig (Linux / Docker)
    candidates = [
        "WenQuanYi Zen Hei",
        "WenQuanYi Micro Hei",
        "Noto Sans CJK SC",
        "Source Han Sans CN",
        "Droid Sans Fallback",
    ]
    if shutil.which("fc-list"):
        try:
            r = subprocess.run(["fc-list", ":lang=zh", "family"], capture_output=True, text=True, timeout=5)
            installed = r.stdout.lower()
            for cand in candidates:
                if cand.lower() in installed:
                    print(f"  🔤 Subtitle font selected (fontconfig): {cand}")
                    return cand
        except Exception:
            pass

    # 2. Check standard Linux font paths
    linux_candidates = [
        ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "WenQuanYi Zen Hei"),
        ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "WenQuanYi Micro Hei"),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "Noto Sans CJK SC"),
        ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", "Noto Sans CJK SC"),
        ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", "Droid Sans Fallback"),
    ]
    for p_path, p_name in linux_candidates:
        if Path(p_path).exists():
            print(f"  🔤 Subtitle font selected (Linux path): {p_name}")
            return p_name

    # 3. Check bundled fonts directory (assets/fonts)
    bundled_fonts_dir = ASSETS_DIR / "fonts"
    if bundled_fonts_dir.exists():
        for font_file in bundled_fonts_dir.glob("*"):
            fname = font_file.name.lower()
            if "wqy" in fname or "zenhei" in fname:
                print("  🔤 Subtitle font selected (bundled): WenQuanYi Zen Hei")
                return "WenQuanYi Zen Hei"
            elif "noto" in fname:
                return "Noto Sans CJK SC"

    print("  🔤 Subtitle font fallback (Linux): WenQuanYi Zen Hei")
    return "WenQuanYi Zen Hei"


def chunk_chinese_text(text: str, max_chars: int = 9) -> List[str]:
    """
    Break continuous Chinese text into short, natural rhythmic visual subtitle chunks.
    Splits by clauses (punctuation) and ensures chunks are readable on vertical video (6-10 chars).
    """
    raw_clauses = re.split(r"([，。！？；：\n]+)", text)
    clauses = []
    i = 0
    while i < len(raw_clauses):
        seg = raw_clauses[i].strip()
        if not seg:
            i += 1
            continue
        # If followed immediately by punctuation, attach it
        if i + 1 < len(raw_clauses) and re.match(r"^[，。！？；：\n]+$", raw_clauses[i + 1]):
            seg += raw_clauses[i + 1].strip()
            i += 2
        else:
            i += 1
        clauses.append(seg)

    chunks = []
    for c in clauses:
        if len(c) <= max_chars:
            chunks.append(c)
        else:
            for j in range(0, len(c), max_chars):
                piece = c[j:j + max_chars]
                if piece:
                    chunks.append(piece)
    return chunks if chunks else [text]


class SubtitleGenerator:
    """Creates subtitles from scene narration timings adapted to vertical, horizontal, or square canvas."""

    def __init__(
        self,
        output_dir: Path = SUBTITLES_DIR,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        margin_bottom: int = SUBTITLE_MARGIN_BOTTOM,
        font_size: int = SUBTITLE_FONT_SIZE,
        dynamic_highlight: bool = SUBTITLE_DYNAMIC,
        highlight_color: str = SUBTITLE_HIGHLIGHT_COLOR,
    ):
        self.output_dir = Path(output_dir)
        self.width = width
        self.height = height
        self.margin_bottom = margin_bottom
        self.font_size = font_size
        self.dynamic_highlight = dynamic_highlight
        self.highlight_color = highlight_color
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_subtitles(
        self,
        scene_timings: List[Dict[str, Any]],
        max_words_per_line: Optional[int] = None,
        language: str = "es",
        custom_font: Optional[str] = None,
        source_attributions: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[Path, Path]:
        """
        Generate both SRT and styled ASS subtitle files.
        Splits scene narrations into short, rhythmic chunks adapted to canvas aspect ratio.
        Optionally renders professional source attribution badges (e.g. NASA APOD, NASA Library).
        """
        subtitle_chunks: List[Dict[str, Any]] = []

        is_wide = self.width > self.height
        if max_words_per_line is None:
            max_words = 6 if is_wide else 4
        else:
            max_words = max_words_per_line

        max_cjk_chars = 10 if is_wide else 6

        for scene in scene_timings:
            narration = scene.get("narration", "").strip()
            start_time = scene.get("start", 0.0)
            end_time = scene.get("end", start_time + 4.0)
            duration = max(0.5, end_time - start_time)

            if not narration:
                continue

            if is_cjk(narration) or (language or "").lower().startswith("zh"):
                groups = chunk_chinese_text(narration, max_chars=max_cjk_chars)
            else:
                words = narration.split()
                if not words:
                    continue
                total_words = len(words)
                chunk_size = min(max_words, max(2, math.ceil(total_words / max(1, duration / 1.3))))
                groups = [" ".join(words[i:i + chunk_size]) for i in range(0, total_words, chunk_size)]

            num_groups = len(groups)
            if num_groups == 0:
                continue

            chunk_duration = duration / num_groups
            for idx, group_text in enumerate(groups):
                chunk_start = start_time + (idx * chunk_duration)
                chunk_end = min(end_time, chunk_start + chunk_duration)
                display_text = group_text if is_cjk(group_text) else group_text.upper()

                subtitle_chunks.append({
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": display_text
                })

        srt_path = self.output_dir / "subtitles.srt"
        ass_path = self.output_dir / "subtitles.ass"

        self._write_srt(subtitle_chunks, srt_path)
        self._write_ass(
            subtitle_chunks,
            ass_path,
            language=language,
            custom_font=custom_font,
            source_attributions=source_attributions
        )

        print(f"  📝 Subtitles generated: {srt_path.name} & {ass_path.name} ({len(subtitle_chunks)} cues, dynamic={self.dynamic_highlight})")
        return srt_path, ass_path

    def _write_srt(self, chunks: List[Dict[str, Any]], file_path: Path) -> None:
        """Write standard SRT format without formatting tags for maximum player compatibility."""
        with open(file_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks, 1):
                start_str = format_timestamp_srt(chunk["start"])
                end_str = format_timestamp_srt(chunk["end"])
                f.write(f"{i}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{chunk['text']}\n\n")

    def _write_ass(
        self,
        chunks: List[Dict[str, Any]],
        file_path: Path,
        language: str = "es",
        custom_font: Optional[str] = None,
        source_attributions: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Write ASS format with custom styling, dynamic word-by-word active highlight,
        and high-visibility semi-transparent source attribution badges.
        """
        has_cjk = any(is_cjk(c.get("text", "")) for c in chunks)
        is_chinese = has_cjk or (language or "").lower().startswith("zh")
        if is_chinese:
            font_family = resolve_chinese_font(custom_font=custom_font)
            font_size = self.font_size + 2
            bold_val = 0  # Normal weight for CJK prevents font substitution errors on TTC files
            outline_val = 4.0
        else:
            font_family = custom_font if custom_font else SUBTITLE_FONT
            font_size = self.font_size
            bold_val = -1
            outline_val = SUBTITLE_OUTLINE_WIDTH

        # Strictly ensure font_family has NO commas (ASS style fields are comma-separated)
        if "," in font_family:
            font_family = font_family.split(",")[0].strip()

        # Clean highlight color string (e.g. &H0000FFFF&)
        hl_color = self.highlight_color.strip()
        if not hl_color.startswith("&H"):
            hl_color = f"&H{hl_color}"
        if not hl_color.endswith("&"):
            hl_color = f"{hl_color}&"

        # Determine dimensions for SourceBadge (top-left safe zone badge)
        if self.width < self.height:
            # Vertical (Shorts/TikTok/Reels)
            badge_font_size = 28
            badge_margin_x = 60
            badge_margin_y = 110
        elif self.width > self.height:
            # Landscape
            badge_font_size = 22
            badge_margin_x = 50
            badge_margin_y = 50
        else:
            # Square
            badge_font_size = 24
            badge_margin_x = 50
            badge_margin_y = 60

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsDefault,{font_family},{font_size},{SUBTITLE_PRIMARY_COLOR},&H000000FF,{SUBTITLE_OUTLINE_COLOR},&H80000000,{bold_val},0,0,0,100,100,1.2,0,1,{outline_val},2.2,2,80,80,{self.margin_bottom},1
Style: SourceBadge,{font_family},{badge_font_size},&H00FFFFFF,&H000000FF,&H80000000,&H90101010,1,0,0,0,100,100,0.8,0,3,10,0,7,{badge_margin_x},{badge_margin_x},{badge_margin_y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header)

            # 1. Write Source Attribution Badges on Layer 1 (Top-Left overlay with smooth fade)
            if source_attributions:
                for attr in source_attributions:
                    raw_attr_text = (attr.get("text") or "").strip()
                    if not raw_attr_text:
                        continue
                    clean_attr_text = raw_attr_text.replace("\n", " ").strip()
                    clean_attr_text = clean_attr_text.replace("📡", "").strip()
                    if not any(clean_attr_text.startswith(p) for p in ["NASA", "Fuente:", "Crédito:", "Source:"]):
                        clean_attr_text = f"NASA | {clean_attr_text}"

                    attr_start = max(0.0, float(attr.get("start", 0.0)))
                    attr_end = max(attr_start + 1.0, float(attr.get("end", attr_start + 5.0)))
                    f.write(
                        f"Dialogue: 1,{format_timestamp_ass(attr_start)},{format_timestamp_ass(attr_end)},"
                        f"SourceBadge,,0,0,0,,{{\\fad(350,350)}}{clean_attr_text}\n"
                    )

            # 2. Write Spoken Narration Subtitles on Layer 0 (Bottom Center)
            for chunk in chunks:
                raw_text = chunk["text"].strip()
                c_start = chunk["start"]
                c_end = chunk["end"]
                c_dur = max(0.2, c_end - c_start)

                if not raw_text:
                    continue

                if not self.dynamic_highlight:
                    # Static cue
                    start_str = format_timestamp_ass(c_start)
                    end_str = format_timestamp_ass(c_end)
                    clean_text = raw_text.replace("\n", "\\N")
                    f.write(f"Dialogue: 0,{start_str},{end_str},ShortsDefault,,0,0,0,,{clean_text}\n")
                    continue

                # Dynamic word-by-word active highlight
                if is_cjk(raw_text):
                    # For Chinese, break into 2-character subsegments
                    chars = list(raw_text)
                    step = 2
                    segments = ["".join(chars[i:i + step]) for i in range(0, len(chars), step)]
                    seg_count = len(segments)
                    seg_dur = c_dur / max(1, seg_count)

                    for s_idx, seg in enumerate(segments):
                        w_start = c_start + (s_idx * seg_dur)
                        w_end = min(c_end, w_start + seg_dur)
                        # Highlight current segment
                        parts = []
                        for j_idx, other_seg in enumerate(segments):
                            if j_idx == s_idx:
                                parts.append(f"{{\\c{hl_color}\\b1}}{other_seg}{{\\rShortsDefault}}")
                            else:
                                parts.append(other_seg)
                        line_text = "".join(parts)
                        f.write(f"Dialogue: 0,{format_timestamp_ass(w_start)},{format_timestamp_ass(w_end)},ShortsDefault,,0,0,0,,{line_text}\n")
                else:
                    words = raw_text.split()
                    word_count = len(words)
                    if word_count <= 1:
                        start_str = format_timestamp_ass(c_start)
                        end_str = format_timestamp_ass(c_end)
                        line_text = f"{{\\c{hl_color}\\b1}}{raw_text}{{\\rShortsDefault}}"
                        f.write(f"Dialogue: 0,{start_str},{end_str},ShortsDefault,,0,0,0,,{line_text}\n")
                    else:
                        # Distribute duration by character weight
                        weights = [max(2, len(w)) for w in words]
                        tot_weight = sum(weights)
                        cur_w_start = c_start

                        for w_idx, word in enumerate(words):
                            w_slice = (weights[w_idx] / tot_weight) * c_dur
                            w_end = min(c_end, cur_w_start + w_slice)

                            # Format phrase with current active word highlighted
                            line_parts = []
                            for j, w in enumerate(words):
                                if j == w_idx:
                                    line_parts.append(f"{{\\c{hl_color}\\b1}}{w}{{\\rShortsDefault}}")
                                else:
                                    line_parts.append(w)

                            line_text = " ".join(line_parts)
                            f.write(f"Dialogue: 0,{format_timestamp_ass(cur_w_start)},{format_timestamp_ass(w_end)},ShortsDefault,,0,0,0,,{line_text}\n")
                            cur_w_start = w_end

