"""
Robo Agents Video Renderer.
Composites background stock videos, transparent robot avatars, 
dynamic speech bubbles, and Edge TTS audio into high-retention vertical MP4 shorts.
"""

import os
import shutil
import subprocess
import textwrap
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from PIL import Image, ImageDraw, ImageFont

from config import (
    ASSETS_DIR,
    AUDIO_CODEC,
    OUTPUT_DIR,
    TEMP_DIR,
    VIDEO_CODEC,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)
from providers.pexels import PexelsProvider
from providers.pixabay import PixabayProvider
from utils.files import get_media_duration


def find_system_font(size: int = 42) -> ImageFont.FreeTypeFont:
    """Load DejaVuSans or fallback system font."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


class RoboRenderer:
    """Renders dual-robot animated dialogue videos using PIL and FFmpeg."""

    def __init__(
        self,
        pexels_provider: Optional[PexelsProvider] = None,
        pixabay_provider: Optional[PixabayProvider] = None,
        temp_dir: Path = TEMP_DIR,
        output_dir: Path = OUTPUT_DIR,
    ):
        self.pexels = pexels_provider or PexelsProvider()
        self.pixabay = pixabay_provider or PixabayProvider()
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Asset paths
        self.assets_dir = Path(__file__).parent / "assets"
        self.orange_png_path = self.assets_dir / "orange_bot.png"
        self.blue_png_path = self.assets_dir / "blue_bot.png"

        self._load_bot_images()

    def _load_bot_images(self):
        """Load and resize robot PNGs."""
        bot_size = (400, 400)
        if self.orange_png_path.exists():
            self.orange_bot = Image.open(self.orange_png_path).convert("RGBA").resize(bot_size, Image.Resampling.LANCZOS)
        else:
            self.orange_bot = Image.new("RGBA", bot_size, (255, 140, 0, 255))

        if self.blue_png_path.exists():
            self.blue_bot = Image.open(self.blue_png_path).convert("RGBA").resize(bot_size, Image.Resampling.LANCZOS)
        else:
            self.blue_bot = Image.new("RGBA", bot_size, (0, 162, 255, 255))

    def create_turn_overlay(
        self,
        speaker: str,
        text: str,
        turn_num: int,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
    ) -> Path:
        """
        Renders a transparent PNG overlay containing:
        - Orange Robot (bottom left)
        - Blue Robot (bottom right)
        - Highlight on active speaker
        - Dynamic text speech bubble pointing to active speaker
        """
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        is_orange = speaker.lower() == "orange"

        # 1. Position Avatars (Bottom zone)
        # Active speaker is placed slightly higher & full opacity; idle speaker is slightly lower & dimmer
        orange_y = 1320 if is_orange else 1360
        blue_y = 1320 if not is_orange else 1360

        orange_img = self.orange_bot.copy()
        blue_img = self.blue_bot.copy()

        if not is_orange:
            # Dim orange slightly when blue speaks
            r, g, b, a = orange_img.split()
            a = a.point(lambda p: int(p * 0.55))
            orange_img.putalpha(a)
        else:
            # Dim blue slightly when orange speaks
            r, g, b, a = blue_img.split()
            a = a.point(lambda p: int(p * 0.55))
            blue_img.putalpha(a)

        overlay.paste(orange_img, (60, orange_y), orange_img)
        overlay.paste(blue_img, (width - 400 - 60, blue_y), blue_img)

        # 2. Character Name Badges
        font_badge = find_system_font(32)
        # Orange badge
        draw.rounded_rectangle([70, orange_y + 390, 270, orange_y + 440], radius=15, fill=(255, 140, 0, 230))
        draw.text((105, orange_y + 396), "ORANGE", font=font_badge, fill=(255, 255, 255, 255))
        # Blue badge
        draw.rounded_rectangle([width - 270, blue_y + 390, width - 70, blue_y + 440], radius=15, fill=(0, 140, 255, 230))
        draw.text((width - 225, blue_y + 396), "BLUE", font=font_badge, fill=(255, 255, 255, 255))

        # 3. Speech Bubble Rendering
        font_text = find_system_font(44)
        wrapped_lines = textwrap.wrap(text, width=24)
        line_height = 54
        text_height = len(wrapped_lines) * line_height

        bubble_w = 940
        bubble_h = max(220, text_height + 80)
        bubble_x = (width - bubble_w) // 2
        bubble_y = 960 - (bubble_h // 2)

        # Speech bubble box with rounded corners
        bg_color = (255, 255, 255, 245)
        border_color = (255, 140, 0, 255) if is_orange else (0, 162, 255, 255)
        draw.rounded_rectangle(
            [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
            radius=35,
            fill=bg_color,
            outline=border_color,
            width=6,
        )

        # Bubble Tail pointing down towards speaker
        if is_orange:
            tail_pts = [
                (bubble_x + 160, bubble_y + bubble_h - 2),
                (bubble_x + 200, bubble_y + bubble_h + 45),
                (bubble_x + 250, bubble_y + bubble_h - 2),
            ]
        else:
            tail_pts = [
                (bubble_x + bubble_w - 250, bubble_y + bubble_h - 2),
                (bubble_x + bubble_w - 200, bubble_y + bubble_h + 45),
                (bubble_x + bubble_w - 160, bubble_y + bubble_h - 2),
            ]

        draw.polygon(tail_pts, fill=bg_color, outline=border_color)

        # Render dialogue text inside bubble
        curr_y = bubble_y + (bubble_h - text_height) // 2
        for line in wrapped_lines:
            # Measure line width using textbbox
            bbox = draw.textbbox((0, 0), line, font=font_text)
            w_line = bbox[2] - bbox[0]
            curr_x = bubble_x + (bubble_w - w_line) // 2
            draw.text((curr_x, curr_y), line, font=font_text, fill=(15, 15, 15, 255))
            curr_y += line_height

        overlay_file = self.temp_dir / f"robo_overlay_{turn_num:02d}.png"
        overlay.save(overlay_file)
        return overlay_file

    def fetch_background_video(self, keywords: List[str], duration: float, turn_idx: int) -> Path:
        """Fetch stock background video from Pexels or Pixabay."""
        # Try Pexels first
        if self.pexels.is_configured():
            asset_file, _ = self.pexels.fetch_scene_asset(
                scene_idx=turn_idx,
                keywords=keywords,
                preferred_type="video",
                save_dir=self.temp_dir,
                orientation="portrait"
            )
            if asset_file and asset_file.exists():
                return asset_file

        # Try Pixabay second
        if self.pixabay.is_configured():
            asset_file, _ = self.pixabay.fetch_scene_asset(
                scene_idx=turn_idx,
                keywords=keywords,
                preferred_type="video",
                save_dir=self.temp_dir,
                orientation="portrait"
            )
            if asset_file and asset_file.exists():
                return asset_file

        # Fallback background generation: procedurally generated dark animated background
        video_clip = self.temp_dir / f"bg_raw_{turn_idx:02d}.mp4"
        print(f"  ℹ️ Stock video download unavailable for turn {turn_idx}. Generating dark space fallback canvas.")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x0B0E14:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d={duration:.2f}",
            "-c:v", VIDEO_CODEC,
            "-pix_fmt", "yuv420p",
            str(video_clip)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return video_clip

    def render_turn_clip(self, turn: Dict[str, Any], turn_idx: int) -> Path:
        """
        Renders an individual turn MP4 clip combining background video, overlay PNG, and spoken audio.
        """
        output_clip = self.temp_dir / f"robo_turn_clip_{turn_idx:02d}.mp4"
        duration = turn["duration"]
        speaker = turn["speaker"]
        text = turn["text"]
        audio_path = turn["audio_path"]
        keywords = turn.get("keywords", ["space", "technology"])

        # 1. Fetch background video
        bg_video = self.fetch_background_video(keywords, duration, turn_idx)

        # 2. Render Overlay PNG
        overlay_png = self.create_turn_overlay(speaker, text, turn_idx)

        # 3. FFmpeg composition: rescale background to 1080x1920 vertical & overlay PNG
        filter_complex = (
            f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,fps={VIDEO_FPS}[bg];"
            f"[bg][1:v]overlay=0:0[outv]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(bg_video),
            "-i", str(overlay_png),
            "-i", str(audio_path),
            "-t", f"{duration:.2f}",
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "2:a",
            "-c:v", VIDEO_CODEC,
            "-preset", "fast",
            "-crf", "18",
            "-c:a", AUDIO_CODEC,
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(output_clip)
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output_clip

    def assemble_final_video(self, turn_clips: List[Path], topic: str) -> Path:
        """
        Concatenates turn clips into final MP4 video in output folder.
        """
        concat_list = self.temp_dir / "concat_robo_list.txt"
        with open(concat_list, "w", encoding="utf-8") as f:
            for clip in turn_clips:
                f.write(f"file '{clip.resolve()}'\n")

        timestamp = int(time.time())
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:25]
        output_file = self.output_dir / f"robo_agents_{safe_topic}_{timestamp}.mp4"

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_file)
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"\n🎬 Final Robo Agents Video successfully rendered!\n📁 File: {output_file}")
        return output_file
