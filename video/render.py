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
import random
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import (
    ASSETS_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    VIDEO_CODEC,
    AUDIO_CODEC,
    VIDEO_BITRATE,
    AUDIO_BITRATE,
    OUTPUT_DIR,
    TEMP_DIR,
    ENABLE_TRANSITIONS,
    DEFAULT_TRANSITION,
    TRANSITION_DURATION,
    SUPPORTED_TRANSITIONS,
    ENABLE_SFX,
    SFX_VOLUME,
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
        is_video: bool = False,
        transition_pad: float = 0.0
    ) -> Path:
        """
        Render an individual scene visual clip formatted to target dimensions.
        transition_pad adds extra head/tail frames so visual crossfades don't shorten audio sync.
        Applies varied camera motion patterns across scenes for static images.
        """
        output_clip = self.temp_dir / f"clip_{scene_idx:02d}.mp4"
        clip_duration = duration + transition_pad

        if is_video:
            # Loop short videos if needed, center crop to target format
            filter_chain = (
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height},"
                f"setsar=1,fps={self.fps}"
            )
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", str(asset_path),
                "-t", f"{clip_duration:.2f}",
                "-vf", filter_chain,
                "-c:v", VIDEO_CODEC,
                "-preset", "veryfast",
                "-b:v", VIDEO_BITRATE,
                "-pix_fmt", "yuv420p",
                "-an",
                str(output_clip)
            ]
        else:
            # Static image: Apply documentary-grade varied Ken Burns camera movements
            total_frames = int(self.fps * clip_duration)
            pattern = (scene_idx - 1) % 5

            if pattern == 0:
                # Smooth center zoom in (1.0 -> 1.18)
                zoom_expr = "z='min(zoom+0.0013,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif pattern == 1:
                # Reveal zoom out (1.18 -> 1.0)
                zoom_expr = "z='if(lte(zoom,1.0),1.18,max(1.001,zoom-0.0013))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif pattern == 2:
                # Slow cinematic pan right
                zoom_expr = f"z='1.12':x='(iw-iw/zoom)*(on/{max(1, total_frames)})':y='ih/2-(ih/zoom/2)'"
            elif pattern == 3:
                # Slow cinematic pan left
                zoom_expr = f"z='1.12':x='(iw-iw/zoom)*(1-on/{max(1, total_frames)})':y='ih/2-(ih/zoom/2)'"
            else:
                # Subtle upward tilt
                zoom_expr = f"z='1.12':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{max(1, total_frames)})'"

            filter_chain = (
                f"scale={self.width*2}:{self.height*2}:force_original_aspect_ratio=increase,"
                f"zoompan={zoom_expr}:d={total_frames}:s={self.width}x{self.height}:fps={self.fps},"
                f"setsar=1"
            )
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(asset_path),
                "-t", f"{clip_duration:.2f}",
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
        except subprocess.CalledProcessError:
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
                "-t", f"{clip_duration:.2f}",
                "-vf", fallback_filter,
                "-c:v", VIDEO_CODEC,
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-an",
                str(output_clip)
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return output_clip

    def render_emergency_color_clip(self, duration: float, scene_idx: int, transition_pad: float = 0.0) -> Path:
        """Generate a space-dark gradient background if an asset fails to download."""
        output_clip = self.temp_dir / f"clip_{scene_idx:02d}.mp4"
        clip_duration = duration + transition_pad
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x070b19:s={self.width}x{self.height}:r={self.fps}:d={clip_duration:.2f}",
            "-c:v", VIDEO_CODEC,
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_clip)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output_clip

    def assemble_visual_clips(
        self,
        scene_clips: List[Path],
        scene_durations: Optional[List[float]] = None,
        transition: str = DEFAULT_TRANSITION,
        transition_duration: float = TRANSITION_DURATION
    ) -> Path:
        """
        Concatenate visual scene clips with smooth FFmpeg xfade transitions.
        Falls back to standard concat if transitions are disabled or xfade is not applicable.
        """
        raw_video_path = self.temp_dir / "combined_visuals.mp4"
        num_clips = len(scene_clips)

        # If transitions disabled, only 1 clip, or transition is 'none': use fast concat demuxer
        if num_clips <= 1 or transition == "none" or not ENABLE_TRANSITIONS or not scene_durations or len(scene_durations) != num_clips:
            concat_file = self.temp_dir / "video_concat.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                for clip in scene_clips:
                    f.write(f"file '{clip.resolve()}'\n")

            concat_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                str(raw_video_path)
            ]
            subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return raw_video_path

        # Assemble with FFmpeg xfade filter complex
        print(f"  ✨ Applying '{transition}' transitions between {num_clips} scenes ({transition_duration:.2f}s crossfades)...")
        filter_parts = []
        current_offset = 0.0

        for i in range(1, num_clips):
            current_offset += scene_durations[i - 1]

            if transition == "random":
                cur_trans = random.choice(["fade", "dissolve", "wipeleft", "slideleft", "smoothleft", "circleopen"])
            elif transition in SUPPORTED_TRANSITIONS:
                cur_trans = transition
            else:
                cur_trans = "fade"

            in_a = "[0:v]" if i == 1 else f"[v{i-1}]"
            in_b = f"[{i}:v]"
            out_label = "[vout]" if i == num_clips - 1 else f"[v{i}]"

            filter_parts.append(
                f"{in_a}{in_b}xfade=transition={cur_trans}:duration={transition_duration:.2f}:offset={current_offset:.2f}{out_label}"
            )

        filter_complex_str = ";".join(filter_parts)

        cmd = ["ffmpeg", "-y"]
        for clip in scene_clips:
            cmd.extend(["-i", str(clip.resolve())])

        cmd.extend([
            "-filter_complex", filter_complex_str,
            "-map", "[vout]",
            "-c:v", VIDEO_CODEC,
            "-preset", "veryfast",
            "-b:v", VIDEO_BITRATE,
            "-pix_fmt", "yuv420p",
            "-an",
            str(raw_video_path)
        ])

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if raw_video_path.exists() and raw_video_path.stat().st_size > 0:
                return raw_video_path
        except subprocess.CalledProcessError as e:
            print("  ⚠️ xfade transition filter warning, falling back to seamless concat...")
            concat_file = self.temp_dir / "video_concat.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                for clip in scene_clips:
                    f.write(f"file '{clip.resolve()}'\n")

            concat_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                str(raw_video_path)
            ]
            subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return raw_video_path

    def assemble_final_video(
        self,
        scene_clips: List[Path],
        narration_audio: Path,
        subtitles_file: Optional[Path],
        output_filename: str,
        background_music: Optional[Path] = None,
        sfx_track: Optional[Path] = None,
        assets_metadata: Optional[List[Dict[str, Any]]] = None,
        output_dir: Optional[Path] = None,
        language: str = "es",
        scene_durations: Optional[List[float]] = None,
        transition: str = DEFAULT_TRANSITION,
        transition_duration: float = TRANSITION_DURATION
    ) -> Path:
        """
        Concatenate visual scene clips with transitions, mix audio tracks (voice, music, SFX),
        burn styled subtitles, and render final production-ready MP4.
        """
        if not check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not found in system PATH.")

        target_dir = Path(output_dir) if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        final_output_path = target_dir / output_filename
        print(f"\n🎬 Rendering final video: {final_output_path.name} ({self.width}x{self.height})...")

        # 1. Assemble visual clips (with xfade transitions if enabled)
        raw_video_path = self.assemble_visual_clips(
            scene_clips=scene_clips,
            scene_durations=scene_durations,
            transition=transition,
            transition_duration=transition_duration
        )

        # 2. Prepare audio mixing (Voice 1.0, Music 0.12, SFX volume)
        cmd = ["ffmpeg", "-y", "-i", str(raw_video_path), "-i", str(narration_audio)]
        filter_complex = []

        audio_parts = ["[1:a]volume=1.0[voice]"]
        mix_inputs = ["[voice]"]
        input_idx = 2

        if background_music and background_music.exists():
            cmd.extend(["-i", str(background_music)])
            audio_parts.append(f"[{input_idx}:a]volume=0.12[bg]")
            mix_inputs.append("[bg]")
            input_idx += 1

        if sfx_track and sfx_track.exists():
            cmd.extend(["-i", str(sfx_track)])
            audio_parts.append(f"[{input_idx}:a]volume={SFX_VOLUME:.2f}[sfx]")
            mix_inputs.append("[sfx]")
            input_idx += 1

        if len(mix_inputs) > 1:
            mix_chain = "".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:duration=first[aout]"
            filter_complex.append(";".join(audio_parts) + ";" + mix_chain)
        else:
            filter_complex.append("[1:a]volume=1.0[aout]")

        # 3. Subtitles burning
        subtitle_filter = ""
        if subtitles_file and subtitles_file.exists():
            sub_path_escaped = str(subtitles_file.resolve()).replace(":", "\\:")

            # Check if assets/fonts contains bundled font files (e.g. CJK fonts)
            fonts_param = ""
            fonts_dir = ASSETS_DIR / "fonts"
            if fonts_dir.exists() and any(fonts_dir.iterdir()):
                fonts_escaped = str(fonts_dir.resolve()).replace(":", "\\:")
                fonts_param = f":fontsdir='{fonts_escaped}'"

            if subtitles_file.suffix == ".ass":
                subtitle_filter = f"ass='{sub_path_escaped}'{fonts_param}"
            else:
                subtitle_filter = f"subtitles='{sub_path_escaped}'{fonts_param}"

        if subtitle_filter:
            filter_complex.append(f"[0:v]{subtitle_filter}[vout]")
        else:
            filter_complex.append("[0:v]copy[vout]")

        filter_str = ";".join(filter_complex)

        final_cmd = [
            "ffmpeg", "-y",
            *cmd[2:],  # All inputs
            "-filter_complex", filter_str,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", VIDEO_CODEC,
            "-preset", "veryfast",
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
            err_msg = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
            print(f"  ⚠️ Subtitle filter warning ({err_msg[:120]}), rendering fallback stream...")
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
                "language": language,
                "resolution": f"{self.width}x{self.height}",
                "fps": self.fps,
                "total_scenes": len(scene_clips),
                "transitions": transition,
                "sfx_enabled": bool(sfx_track and sfx_track.exists()),
                "media_sources": assets_metadata,
                "nasa_sources": assets_metadata
            }
            meta_output_file = target_dir / "metadata.json"
            save_json(meta_data, meta_output_file)
            save_json(meta_data, target_dir / "source_metadata.json")
            print(f"  📄 Source provenance saved to: {meta_output_file.name}")

        print(f"✨ Video successfully rendered: {final_output_path}")
        return final_output_path

