"""
GCP NotebookLM Video Builder.
Assembles two-host technical debate audio, synchronized vector slides,
captions, and ambient sound into a finished 1080p MP4 tutorial video.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from config import (
    BASE_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    VIDEO_FPS,
    VIDEO_CRF,
    VIDEO_PRESET,
    MUSIC_DIR
)
from utils.files import get_media_duration
from utils.fonts import resolve_best_font_path
from video.slide_renderer import GCPSlideRenderer


def wrap_text_for_subtitles(text: str, max_chars_per_line: int = 68) -> str:
    """Wraps dialogue text cleanly into readable subtitle lines without splitting words."""
    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 > max_chars_per_line and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + 1
    if current_line:
        lines.append(" ".join(current_line))
    return "\n".join(lines)


class GCPVideoBuilder:
    """Builds full audiovisual tutorials from lesson specifications."""

    def __init__(
        self,
        output_dir: Path = OUTPUT_DIR / "gcp_tutorials",
        temp_dir: Path = TEMP_DIR / "gcp_build",
        width: int = 1920,
        height: int = 1080,
        burn_subtitles: bool = True,
        enable_music: bool = True
    ):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.width = width
        self.height = height
        self.burn_subtitles = burn_subtitles
        self.enable_music = enable_music
        self.slide_renderer = GCPSlideRenderer(width, height)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def build_tutorial_video(
        self,
        lesson: Dict[str, Any],
        output_file_name: Optional[str] = None
    ) -> Path:
        """
        Orchestrates full rendering:
        1. Synthesizes dialogue turns with Alex & Sam voices.
        2. Renders slide PNG frames with active host indicators.
        3. Encodes synchronized video segments.
        4. Concatenates segments and mixes background ambiance.
        5. Returns final MP4 video path.
        """
        topic_slug = lesson.get("topic", "gcp_tutorial").lower().replace(" ", "_")
        topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "_")[:32]
        
        target_name = output_file_name or f"tutorial_{topic_slug}.mp4"
        final_video_path = self.output_dir / target_name

        slides_dict = {s["slide_id"]: s for s in lesson.get("slides", [])}
        dialogue_turns = lesson.get("dialogue", [])
        total_slides = len(slides_dict)

        print(f"\n🚀 [GCP Video Builder] Iniciando renderizado de: '{lesson.get('title')}'")
        print(f"   • Diapositivas técnicas: {total_slides}")
        print(f"   • Turnos de debate: {len(dialogue_turns)}")
        print(f"   • Resolución: {self.width}x{self.height} ({'16:9 Horizontal' if self.width > self.height else '9:16 Vertical'})")

        # Step 1: Synthesize all dialogue turns
        turn_assets: List[Dict[str, Any]] = []
        audio_dir = self.temp_dir / "audio"
        slides_cache_dir = self.temp_dir / "slides"
        segments_dir = self.temp_dir / "segments"

        audio_dir.mkdir(parents=True, exist_ok=True)
        slides_cache_dir.mkdir(parents=True, exist_ok=True)
        segments_dir.mkdir(parents=True, exist_ok=True)

        # Export high-res slides for user inspection
        user_slides_export_dir = self.output_dir / f"{topic_slug}_slides"
        user_slides_export_dir.mkdir(parents=True, exist_ok=True)

        for s_id, s_data in slides_dict.items():
            svg_standalone = self.slide_renderer.render_slide_svg(
                slide=s_data,
                active_speaker="Alex",
                current_slide_num=s_id,
                total_slides=total_slides,
                series_category=lesson.get("category", "Google Cloud Architecture")
            )
            export_png = user_slides_export_dir / f"slide_{s_id:02d}.png"
            self.slide_renderer.rasterize_svg_to_png(svg_standalone, export_png)

        print(f"   🖼️ Diapositivas HD exportadas a: {user_slides_export_dir}")

        print("\n🎙️ [Audio & TTS] Sintetizando debate multipersona...")
        for idx, turn in enumerate(dialogue_turns, start=1):
            speaker = turn.get("speaker", "Alex").capitalize()
            slide_id = turn.get("slide_id", 1)
            dialogue_text = turn.get("text", "")

            slide_data = slides_dict.get(slide_id, list(slides_dict.values())[0])

            # 1. Synthesize audio
            audio_path = audio_dir / f"turn_{idx:02d}_{speaker.lower()}.mp3"
            self._synthesize_host_voice(speaker, dialogue_text, audio_path)

            duration = get_media_duration(audio_path)
            duration = max(duration, 3.2)  # Minimum readable duration

            # 2. Render slide image with active speaker indicator
            slide_svg = self.slide_renderer.render_slide_svg(
                slide=slide_data,
                active_speaker=speaker,
                current_slide_num=slide_id,
                total_slides=total_slides,
                series_category=lesson.get("category", "Google Cloud Architecture")
            )
            slide_img_path = slides_cache_dir / f"frame_{idx:02d}_{speaker.lower()}.png"
            self.slide_renderer.rasterize_svg_to_png(slide_svg, slide_img_path)

            turn_assets.append({
                "turn_id": idx,
                "speaker": speaker,
                "slide_id": slide_id,
                "text": dialogue_text,
                "audio_path": audio_path,
                "slide_img": slide_img_path,
                "duration": duration
            })

            print(f"   • [{speaker} | Slide {slide_id:02d}] {duration:.1f}s — \"{dialogue_text[:40]}...\"")

        # Step 2: Render individual video segments with FFmpeg
        print("\n🎬 [FFmpeg Encoding] Renderizando segmentos de diapositivas sincronizadas...")
        segment_files: List[Path] = []
        for asset in turn_assets:
            idx = asset["turn_id"]
            dur = asset["duration"]
            img = asset["slide_img"]
            aud = asset["audio_path"]
            seg_out = segments_dir / f"segment_{idx:02d}.mp4"

            # Optional burned subtitles
            subtitle_filter = ""
            if self.burn_subtitles:
                subs_dir = self.temp_dir / "subtitles"
                subs_dir.mkdir(parents=True, exist_ok=True)
                sub_file = subs_dir / f"caption_{idx:02d}.txt"
                wrapped_caption = wrap_text_for_subtitles(f"[{asset['speaker'].upper()}]: {asset['text']}")
                sub_file.write_text(wrapped_caption, encoding="utf-8")
                escaped_sub_path = str(sub_file.resolve()).replace("\\", "/").replace(":", "\\:")
                font_param, _ = resolve_best_font_path()
                subtitle_filter = (
                    f",drawtext={font_param}:textfile='{escaped_sub_path}':"
                    f"fontcolor=white:fontsize=22:line_spacing=6:box=1:boxcolor=0x000000@0.80:boxborderw=10:"
                    f"x=(w-text_w)/2:y=h-155"
                )

            vf_string = f"scale={self.width}:{self.height},format=yuv420p{subtitle_filter}"

            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-t", f"{dur:.2f}",
                "-i", str(img),
                "-i", str(aud),
                "-vf", vf_string,
                "-c:v", "libx264",
                "-preset", VIDEO_PRESET,
                "-crf", str(VIDEO_CRF),
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(seg_out)
            ]
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as err:
                err_log = err.stderr.decode("utf-8", errors="ignore") if err.stderr else ""
                print(f"\n❌ Error codificando segmento {idx:02d} con FFmpeg:\n{err_log[-800:]}")
                raise err
            segment_files.append(seg_out)

        # Step 3: Concat all segments into a single master video
        print("\n🎞️ [Stitching] Ensamblando video tutorial final...")
        concat_list_file = self.temp_dir / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for s in segment_files:
                f.write(f"file '{s.resolve()}'\n")

        raw_stitched_video = self.temp_dir / "raw_stitched.mp4"
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c", "copy",
            str(raw_stitched_video)
        ]
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Step 4: Optional ambient tech soundtrack mix
        bg_music = self._find_ambient_soundtrack()
        if self.enable_music and bg_music and bg_music.exists():
            print(f"   🎶 Añadiendo música ambiental lo-fi tech: {bg_music.name}")
            total_dur = sum(a["duration"] for a in turn_assets)
            cmd_mix = [
                "ffmpeg", "-y",
                "-i", str(raw_stitched_video),
                "-stream_loop", "-1",
                "-i", str(bg_music),
                "-filter_complex",
                f"[1:a]volume=0.08,afade=t=out:st={max(0, total_dur - 3)}:d=3[bg];"
                f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                str(final_video_path)
            ]
            subprocess.run(cmd_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            raw_stitched_video.rename(final_video_path)

        # Save metadata summary
        meta_path = self.output_dir / f"{topic_slug}_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": lesson.get("title"),
                "topic": lesson.get("topic"),
                "category": lesson.get("category"),
                "summary": lesson.get("summary"),
                "total_duration": sum(a["duration"] for a in turn_assets),
                "slides_count": total_slides,
                "video_path": str(final_video_path),
                "slides_dir": str(user_slides_export_dir)
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ [Completado Exitosamente] Video tutorial generado:")
        print(f"   📹 Archivo: {final_video_path}")
        print(f"   📂 Diapositivas: {user_slides_export_dir}")
        print(f"   📊 Duración total: {sum(a['duration'] for a in turn_assets):.1f} segundos")

        return final_video_path

    def _synthesize_host_voice(self, speaker: str, text: str, output_path: Path):
        """
        Synthesizes voice with acoustic distinction:
        - Alex (Architect): Neutral grounded vocal tone.
        - Sam (DevOps): Higher, faster and brighter tone via FFmpeg pitch filter.
        """
        from audio.tts import GoogleTTSProvider
        raw_tmp = output_path.parent / f"_raw_{output_path.name}"

        # Step 1: Base TTS synthesis
        tts = GoogleTTSProvider(language="es")
        success = tts.synthesize_text(text, raw_tmp)

        if not success or not raw_tmp.exists():
            # Emergency fallback: create tone
            est_dur = max(3.0, len(text.split()) / 2.6)
            cmd_tone = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(est_dur),
                "-acodec", "libmp3lame",
                str(output_path)
            ]
            subprocess.run(cmd_tone, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return

        # Step 2: Pitch & Persona shaping
        if "sam" in speaker.lower():
            # Sam: Dynamic, slightly higher pitch (+12%), energetic
            cmd_fx = [
                "ffmpeg", "-y",
                "-i", str(raw_tmp),
                "-af", "rubberband=pitch=1.12:tempo=1.03,equalizer=f=3200:width_type=h:width=1000:g=2.5",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_path)
            ]
            subprocess.run(cmd_fx, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            raw_tmp.unlink(missing_ok=True)
        else:
            # Alex: Deep, authoritative, warm chest EQ
            cmd_fx = [
                "ffmpeg", "-y",
                "-i", str(raw_tmp),
                "-af", "bass=g=2.5:f=120:w=0.6,equalizer=f=180:width_type=h:width=80:g=1.8",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_path)
            ]
            subprocess.run(cmd_fx, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            raw_tmp.unlink(missing_ok=True)

    def _find_ambient_soundtrack(self) -> Optional[Path]:
        """Looks for ambient lo-fi / tech audio track."""
        if MUSIC_DIR.exists():
            for ext in ("*.mp3", "*.wav", "*.m4a"):
                tracks = list(MUSIC_DIR.glob(ext))
                if tracks:
                    return tracks[0]
        return None
