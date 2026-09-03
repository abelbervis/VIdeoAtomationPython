"""
High-Performance Vertical Video Renderer using FFmpeg.
Assembles NASA images and videos into a 1080x1920 30FPS MP4 video with:
- Ken Burns motion effects on static images
- Rescaling and center cropping for vertical 9:16 layout
- Scene-by-scene audio narration synchronization
- Subtitle burning in mobile safe zones
- Background music ducking and mixing
- Complete metadata tracking in output/source_metadata.json
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    VIDEO_CODEC,
    AUDIO_CODEC,
    VIDEO_BITRATE,
    AUDIO_BITRATE,
    OUTPUT_DIR,
    TEMP_DIR
)
from utils.files import save_json, check_ffmpeg


class VideoRenderer:
    """Renders final vertical science short videos using FFmpeg directly."""

    def __init__(
        self,
        output_dir: Path = OUTPUT_DIR,
        temp_dir: Path = TEMP_DIR,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        fps: int = VIDEO_FPS
    ):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.width = width
        self.height = height
        self.fps = fps
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def render_scene_clip(
        self,
        asset_path: Path,
        duration: float,
        scene_idx: int,
        is_video: bool = False
    ) -> Path:
        """Render an individual scene visual clip formatted to 1080x1920 @ 30fps."""
        output_clip = self.temp_dir / f"clip_{scene_idx:02d}.mp4"

        if is_video:
            # Loop short videos if needed, center crop to 9:16 vertical
            filter_chain = (
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height},"
                f"setsar=1,fps={self.fps}"
            )
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", str(asset_path),
                "-t", f"{duration:.2f}",
                "-vf", filter_chain,
                "-c:v", VIDEO_CODEC,
                "-preset", "veryfast",
                "-b:v", VIDEO_BITRATE,
                "-pix_fmt", "yuv420p",
                "-an",
                str(output_clip)
            ]
        else:
            # Static image: Apply Ken Burns smooth subtle zoom motion
            total_frames = int(self.fps * duration)
            filter_chain = (
                f"scale={self.width*2}:-1,"
                f"zoompan=z='min(zoom+0.0012,1.18)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={self.width}x{self.height}:fps={self.fps},"
                f"setsar=1"
            )
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(asset_path),
                "-t", f"{duration:.2f}",
                "-vf", filter_chain,
                "-c:v", VIDEO_CODEC,
                "-preset", "veryfast",
                "-b:v", VIDEO_BITRATE,
                "-pix_fmt", "yuv420p",
                "-an",
                str(output_clip)
            ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if output_clip.exists() and output_clip.stat().st_size > 0:
                return output_clip
        except subprocess.CalledProcessError as e:
            # Fallback simple scale if zoompan filter fails on specific image sizes
            print(f"  ⚠️ Motion filter fallback for scene {scene_idx}...")
            fallback_filter = (
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height},setsar=1,fps={self.fps}"
            )
            fallback_cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(asset_path),
                "-t", f"{duration:.2f}",
                "-vf", fallback_filter,
                "-c:v", VIDEO_CODEC,
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-an",
                str(output_clip)
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return output_clip

    def render_emergency_color_clip(self, duration: float, scene_idx: int) -> Path:
        """Generate a space-dark gradient background if an asset fails to download."""
        output_clip = self.temp_dir / f"clip_{scene_idx:02d}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x070b19:s={self.width}x{self.height}:r={self.fps}:d={duration:.2f}",
            "-c:v", VIDEO_CODEC,
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_clip)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output_clip

    def assemble_final_video(
        self,
        scene_clips: List[Path],
        narration_audio: Path,
        subtitles_file: Optional[Path],
        output_filename: str,
        background_music: Optional[Path] = None,
        assets_metadata: Optional[List[Dict[str, Any]]] = None,
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Concatenate visual scene clips, mix audio tracks, burn subtitles, and render MP4.
        """
        if not check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not found in system PATH.")

        target_dir = Path(output_dir) if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        final_output_path = target_dir / output_filename
        print(f"\n🎬 Rendering final vertical video: {final_output_path.name}...")

        # 1. Create concatenation list for video clips
        concat_file = self.temp_dir / "video_concat.txt"
        with open(concat_file, "w", encoding="utf-8") as f:
            for clip in scene_clips:
                f.write(f"file '{clip.resolve()}'\n")

        # 2. Concat raw video
        raw_video_path = self.temp_dir / "combined_visuals.mp4"
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(raw_video_path)
        ]
        subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # 3. Prepare final render with audio mixing and subtitles
        cmd = ["ffmpeg", "-y", "-i", str(raw_video_path), "-i", str(narration_audio)]
        filter_complex = []

        if background_music and background_music.exists():
            cmd.extend(["-i", str(background_music)])
            # Mix voice (1.0 volume) and music (0.12 volume)
            filter_complex.append("[1:a]volume=1.0[voice];[2:a]volume=0.12[bg];[voice][bg]amix=inputs=2:duration=first[aout]")
            audio_map = "-map [aout]"
        else:
            filter_complex.append("[1:a]volume=1.0[aout]")
            audio_map = "-map [aout]"

        # Handle Subtitles burning
        subtitle_filter = ""
        if subtitles_file and subtitles_file.exists():
            sub_path_escaped = str(subtitles_file.resolve()).replace("\\", "/").replace(":", "\\:")
            if subtitles_file.suffix == ".ass":
                subtitle_filter = f"ass='{sub_path_escaped}'"
            else:
                subtitle_filter = f"subtitles='{sub_path_escaped}'"

        if subtitle_filter:
            filter_complex.append(f"[0:v]{subtitle_filter}[vout]")
            video_map = "-map [vout]"
        else:
            video_map = "-map 0:v"

        filter_str = ";".join(filter_complex)

        final_cmd = [
            "ffmpeg", "-y",
            *cmd[2:], # Inputs
            "-filter_complex", filter_str,
            "-map", "[vout]" if subtitle_filter else "0:v",
            "-map", "[aout]",
            "-c:v", VIDEO_CODEC,
            "-preset", "fast",
            "-b:v", VIDEO_BITRATE,
            "-pix_fmt", "yuv420p",
            "-c:a", AUDIO_CODEC,
            "-b:a", AUDIO_BITRATE,
            "-shortest",
            "-movflags", "+faststart",
            str(final_output_path)
        ]

        try:
            subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            print("  ⚠️ Subtitle font filter warning, rendering with clean video stream...")
            # Fallback without subtitle filter if libass/fontconfig is missing
            fallback_cmd = [
                "ffmpeg", "-y",
                "-i", str(raw_video_path),
                "-i", str(narration_audio),
                "-c:v", "copy",
                "-c:a", AUDIO_CODEC,
                "-b:a", AUDIO_BITRATE,
                "-shortest",
                str(final_output_path)
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # 4. Save metadata audit file
        if assets_metadata:
            meta_data = {
                "video_file": final_output_path.name,
                "resolution": f"{self.width}x{self.height}",
                "fps": self.fps,
                "total_scenes": len(scene_clips),
                "media_sources": assets_metadata,
                "nasa_sources": assets_metadata
            }
            meta_output_file = target_dir / "metadata.json"
            save_json(meta_data, meta_output_file)
            save_json(meta_data, target_dir / "source_metadata.json")
            print(f"  📄 Source provenance saved to: {meta_output_file.name}")

        print(f"✨ Video successfully rendered: {final_output_path}")
        return final_output_path
