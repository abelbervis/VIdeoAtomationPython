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
    VIDEO_CRF,
    VIDEO_PRESET,
    AUDIO_BITRATE,
    OUTPUT_DIR,
    TEMP_DIR,
    ENABLE_TRANSITIONS,
    DEFAULT_TRANSITION,
    TRANSITION_DURATION,
    SUPPORTED_TRANSITIONS,
    ENABLE_SFX,
    SFX_VOLUME,
    ENABLE_AUTO_DUCKING,
    DUCKING_THRESHOLD,
    DUCKING_RATIO,
    DUCKING_ATTACK,
    DUCKING_RELEASE,
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
        fps: int = VIDEO_FPS,
        crf: int = VIDEO_CRF,
        preset: str = VIDEO_PRESET
    ):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.width = width
        self.height = height
        self.fps = fps
        self.crf = crf
        self.preset = preset
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
                "-preset", "fast",
                "-crf", "17",
                "-pix_fmt", "yuv420p",
                "-an",
                str(output_clip)
            ]
        else:
            # Static image: Apply documentary-grade Ken Burns camera movements with smooth cinematic easing
            total_frames = int(self.fps * clip_duration)
            d = max(1, total_frames)
            progress = f"(on/{d})"
            # Smoothstep curve (Ease-In-Out: smooth start, organic mid motion, gentle deceleration)
            ease_io = f"({progress}*{progress}*(3-2*{progress}))"

            pattern = (scene_idx - 1) % 5

            if scene_idx == 1:
                # Scene 1 Hook: Energetic Impact Zoom-In with Ease-Out (fast initial punch syncing with intro SFX)
                zoom_expr = f"z='1.0+0.22*sin({progress}*(PI/2))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif pattern == 0:
                # Smooth center zoom in (1.0 -> 1.18) with organic Ease-In-Out
                zoom_expr = f"z='1.0+0.18*{ease_io}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif pattern == 1:
                # Reveal zoom out (1.20 -> 1.02) revealing cosmic scope with Ease-In-Out
                zoom_expr = f"z='1.20-0.18*{ease_io}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif pattern == 2:
                # Cinematic pan right with smooth acceleration/deceleration
                zoom_expr = f"z='1.14':x='(iw-iw/zoom)*{ease_io}':y='ih/2-(ih/zoom/2)'"
            elif pattern == 3:
                # Cinematic pan left with smooth acceleration/deceleration
                zoom_expr = f"z='1.14':x='(iw-iw/zoom)*(1-{ease_io})':y='ih/2-(ih/zoom/2)'"
            else:
                # Subtle upward tilt with smooth acceleration/deceleration
                zoom_expr = f"z='1.14':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-{ease_io})'"

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
                "-preset", "fast",
                "-crf", "17",
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
            "-preset", "fast",
            "-crf", "17",
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
        transition_duration: float = TRANSITION_DURATION,
        auto_ducking: bool = ENABLE_AUTO_DUCKING
    ) -> Path:
        """
        Concatenate visual scene clips with transitions, mix audio tracks (voice, music, SFX),
        apply dynamic sidechain auto-ducking, burn styled subtitles, and render final production-ready MP4.
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

        # 2. Prepare audio mixing with dynamic Sidechain Auto-Ducking
        cmd = ["ffmpeg", "-y", "-i", str(raw_video_path), "-i", str(narration_audio)]
        filter_complex = []

        has_music = bool(background_music and background_music.exists())
        has_sfx = bool(sfx_track and sfx_track.exists())

        bg_input_idx = None
        sfx_input_idx = None
        curr_idx = 2

        if has_music:
            cmd.extend(["-i", str(background_music)])
            bg_input_idx = curr_idx
            curr_idx += 1

        if has_sfx:
            cmd.extend(["-i", str(sfx_track)])
            sfx_input_idx = curr_idx
            curr_idx += 1

        if has_music and auto_ducking:
            # Dynamic Studio-Grade Sidechain Ducking:
            # - Voice is split into [voice_main] (mix) and [voice_sc] (sidechain trigger)
            # - Music gets subtle EQ mid-scoop (1.8kHz) so it never clashes with vocal articulation
            # - Sidechain compressor dips music whenever voice speaks and smoothly swells back up during pauses
            filter_parts = [
                "[1:a]aformat=channel_layouts=stereo,asplit=2[voice_main][voice_sc]",
                f"[{bg_input_idx}:a]aformat=channel_layouts=stereo,equalizer=f=1800:t=q:w=1.5:g=-4.0[bg_eq]",
                f"[bg_eq][voice_sc]sidechaincompress=threshold={DUCKING_THRESHOLD}:ratio={DUCKING_RATIO}:attack={DUCKING_ATTACK}:release={DUCKING_RELEASE}[bg_ducked]"
            ]
            mix_list = ["[voice_main]", "[bg_ducked]"]

            if has_sfx:
                filter_parts.append(f"[{sfx_input_idx}:a]aformat=channel_layouts=stereo,volume=1.0[sfx]")
                mix_list.append("[sfx]")

            mix_chain = "".join(mix_list) + f"amix=inputs={len(mix_list)}:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.98[aout]"
            filter_complex.append(";".join(filter_parts) + ";" + mix_chain)
            print(f"  🎙️ Dynamic Auto-Ducking active (threshold: {DUCKING_THRESHOLD}, ratio: {DUCKING_RATIO}:1, release: {DUCKING_RELEASE}ms)")
        elif has_music or has_sfx:
            # Standard mixing (no sidechain ducking fallback)
            audio_parts = ["[1:a]aformat=channel_layouts=stereo,volume=1.0[voice]"]
            mix_inputs = ["[voice]"]
            if has_music:
                audio_parts.append(f"[{bg_input_idx}:a]aformat=channel_layouts=stereo,volume=1.0[bg]")
                mix_inputs.append("[bg]")
            if has_sfx:
                audio_parts.append(f"[{sfx_input_idx}:a]aformat=channel_layouts=stereo,volume=1.0[sfx]")
                mix_inputs.append("[sfx]")

            mix_chain = "".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.98[aout]"
            filter_complex.append(";".join(audio_parts) + ";" + mix_chain)
        else:
            # Voice only
            filter_complex.append("[1:a]aformat=channel_layouts=stereo,volume=1.0[aout]")

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
            "-preset", self.preset,
            "-crf", str(self.crf),
            "-b:v", VIDEO_BITRATE,
            "-maxrate", "16000k",
            "-bufsize", "24000k",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-colorspace", "bt709",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-g", "60",
            "-keyint_min", "30",
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

