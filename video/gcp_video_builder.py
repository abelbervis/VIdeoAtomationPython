"""
GCP NotebookLM Video Builder - Optimized High-Efficiency Edition.
Features:
- Native Latin American Spanish Voices (Alex: es-US / Sam: es-MX).
- 1.2x Speech Tempo (tight, engaging pace without dead pauses).
- Extreme File Size & Bitrate Optimization:
  * 15 FPS (ideal for vector slides & technical diagrams).
  * -tune stillimage with CRF 26-28.
  * 96 kbps AAC audio compression.
  * Zero Ken Burns blurring / static razor-sharp vector rendering.
- Ultra-Compact, Non-Intrusive Bottom Captions.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ai.speech_normalizer import clean_phonetics_for_speech, split_into_tts_clauses
from config import (
    BASE_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    MUSIC_DIR
)
from utils.files import get_media_duration
from utils.fonts import resolve_best_font_path
from video.slide_renderer import GCPSlideRenderer


def wrap_text_for_subtitles(text: str, max_chars_per_line: int = 80) -> str:
    """Wraps dialogue text cleanly into a compact single-line or 2-line discrete caption."""
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
    return "\n".join(lines[:2])


class GCPVideoBuilder:
    """Builds full audiovisual tutorials with maximum efficiency, 1.2x LatAm speech, and 15fps."""

    def __init__(
        self,
        output_dir: Path = OUTPUT_DIR / "gcp_tutorials",
        temp_dir: Path = TEMP_DIR / "gcp_build",
        width: int = 1920,
        height: int = 1080,
        burn_subtitles: bool = True,
        enable_music: bool = True,
        speech_speed: float = 1.20,
        fps: int = 15,
        crf: int = 26,
        codec: str = "libx264",
        audio_bitrate: str = "96k"
    ):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.width = width
        self.height = height
        self.burn_subtitles = burn_subtitles
        self.enable_music = enable_music
        self.speech_speed = max(1.0, min(1.5, speech_speed))
        self.fps = fps
        self.crf = crf
        self.codec = codec if codec in ("libx265", "libx264") else "libx264"
        self.audio_bitrate = audio_bitrate
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
        1. Phonetic speech normalization & 1.2x LatAm Spanish synthesis.
        2. Dynamic step-by-step vector slide rendering with active highlights.
        3. Static razor-sharp 15 FPS video encoding with CRF 26-28 (95% smaller filesize).
        4. Concatenation and ambient audio auto-ducking.
        """
        topic_slug = lesson.get("topic", "gcp_tutorial").lower().replace(" ", "_")
        topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "_")[:32]
        
        target_name = output_file_name or f"tutorial_{topic_slug}.mp4"
        final_video_path = self.output_dir / target_name

        slides_dict = {s["slide_id"]: s for s in lesson.get("slides", [])}
        dialogue_turns = lesson.get("dialogue", [])
        total_slides = len(slides_dict)

        print(f"\n🚀 [GCP Video Builder v3 • Edición Optimizada]")
        print(f"   • Título: '{lesson.get('title')}'")
        print(f"   • Diapositivas: {total_slides} | Intervenciones: {len(dialogue_turns)}")
        print(f"   • Voces: Español Latinoamericano Neutro (Alex: es-US / Sam: es-MX)")
        print(f"   • Velocidad de locución: {self.speech_speed}x (ritmo ágil sin pausas muertas)")
        print(f"   • Video: {self.width}x{self.height} @ {self.fps} FPS ({self.codec}, CRF {self.crf})")
        print(f"   • Audio: AAC {self.audio_bitrate} (optimización de peso máxima)")

        # Organize turns per slide to track progressive visual highlights
        turns_by_slide: Dict[int, List[int]] = {}
        for idx, turn in enumerate(dialogue_turns):
            s_id = turn.get("slide_id", 1)
            turns_by_slide.setdefault(s_id, []).append(idx)

        audio_dir = self.temp_dir / "audio"
        slides_cache_dir = self.temp_dir / "slides"
        segments_dir = self.temp_dir / "segments"
        subs_dir = self.temp_dir / "subtitles"

        audio_dir.mkdir(parents=True, exist_ok=True)
        slides_cache_dir.mkdir(parents=True, exist_ok=True)
        segments_dir.mkdir(parents=True, exist_ok=True)
        subs_dir.mkdir(parents=True, exist_ok=True)

        # Export high-res master slides for standalone review
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

        # Step 1: Synthesize all dialogue turns with Phonetic Normalizer & 1.2x LatAm
        print(f"\n🎙️ [Audio & TTS] Sintetizando locución en Español Latino a {self.speech_speed}x...")
        turn_assets: List[Dict[str, Any]] = []

        for idx, turn in enumerate(dialogue_turns, start=1):
            speaker = turn.get("speaker", "Alex").capitalize()
            slide_id = turn.get("slide_id", 1)
            dialogue_text = turn.get("text", "")

            slide_data = slides_dict.get(slide_id, list(slides_dict.values())[0])

            # Determine progressive focus index for dynamism
            turn_pos = turns_by_slide.get(slide_id, [idx - 1]).index(idx - 1)
            layout = slide_data.get("layout", "concept_card")

            focus_idx = None
            show_exec = False

            if layout == "comparison_table":
                num_rows = len(slide_data.get("rows", []))
                focus_idx = turn_pos % max(1, num_rows)
            elif layout == "architecture_flow":
                num_steps = len(slide_data.get("steps", []))
                focus_idx = min(turn_pos, max(0, num_steps - 1))
            elif layout == "terminal_code":
                show_exec = (turn_pos > 0)
            elif layout in ("concept_card", "checklist"):
                num_bullets = len(slide_data.get("bullet_points", []))
                focus_idx = turn_pos if turn_pos < num_bullets else num_bullets

            # 1. Synthesize audio with cleaned phonetics and 1.2x tempo
            audio_path = audio_dir / f"turn_{idx:02d}_{speaker.lower()}.mp3"
            self._synthesize_host_voice(speaker, dialogue_text, audio_path)

            duration = get_media_duration(audio_path)
            duration = max(duration, 2.5)

            # 2. Render dynamic slide image with active focal highlight
            slide_svg = self.slide_renderer.render_slide_svg(
                slide=slide_data,
                active_speaker=speaker,
                current_slide_num=slide_id,
                total_slides=total_slides,
                series_category=lesson.get("category", "Google Cloud Architecture"),
                focus_index=focus_idx,
                show_execution=show_exec
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
                "duration": duration,
                "focus_index": focus_idx,
                "show_exec": show_exec
            })

            clean_preview = clean_phonetics_for_speech(dialogue_text)[:42]
            focus_info = f"[Enfoque #{focus_idx + 1}]" if focus_idx is not None else ("[Cloud Shell OK]" if show_exec else "")
            print(f"   • [{speaker} | Slide {slide_id:02d} {focus_info}] {duration:.1f}s ({self.speech_speed}x) — \"{clean_preview}...\"")

        # Step 2: Render individual video segments at 15 FPS with stillimage tuning
        print(f"\n🎬 [FFmpeg Encoding] Renderizando segmentos a {self.fps} FPS con alta compresión...")
        segment_files: List[Path] = []
        font_param, _ = resolve_best_font_path()

        for asset in turn_assets:
            idx = asset["turn_id"]
            dur = asset["duration"]
            img = asset["slide_img"]
            aud = asset["audio_path"]
            spk = asset["speaker"]
            seg_out = segments_dir / f"segment_{idx:02d}.mp4"

            # Resilience check
            if not img.exists() or img.stat().st_size == 0:
                print(f"  ⚠️ Frame ausente detectado ({img.name}), autogenerando fallback...")
                cmd_fb = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=0x0B0F19:s={self.width}x{self.height}:d=1",
                    "-vframes", "1",
                    str(img)
                ]
                subprocess.run(cmd_fb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Compact, non-intrusive subtitle styling
            subtitle_filter = ""
            if self.burn_subtitles:
                sub_file = subs_dir / f"caption_{idx:02d}.txt"
                display_text = asset["text"].replace("`", "").replace("*", "")
                wrapped = wrap_text_for_subtitles(display_text, max_chars_per_line=85)
                sub_file.write_text(wrapped, encoding="utf-8")
                escaped_sub_path = str(sub_file.resolve()).replace("\\", "/").replace(":", "\\:")
                
                # Compact bottom single pill, unobtrusive
                subtitle_filter = (
                    f",drawtext={font_param}:textfile='{escaped_sub_path}':"
                    f"fontcolor=white:fontsize=17:line_spacing=4:box=1:boxcolor=0x000000@0.75:boxborderw=8:"
                    f"x=(w-text_w)/2:y=h-64"
                )

            # Clean static frame with 15 FPS
            vf_string = f"scale={self.width}:{self.height},format=yuv420p{subtitle_filter}"

            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-t", f"{dur:.2f}",
                "-i", str(img),
                "-i", str(aud),
                "-vf", vf_string,
                "-r", str(self.fps),
                "-c:v", self.codec,
                "-preset", "veryfast",
                "-crf", str(self.crf)
            ]

            if self.codec == "libx264":
                cmd.extend(["-tune", "stillimage"])

            cmd.extend([
                "-c:a", "aac",
                "-b:a", self.audio_bitrate,
                "-shortest",
                str(seg_out)
            ])

            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as err:
                err_log = err.stderr.decode("utf-8", errors="ignore") if err.stderr else ""
                print(f"\n❌ Error codificando segmento {idx:02d} con FFmpeg:\n{err_log[-600:]}")
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

        # Step 4: Ambient tech soundtrack mixing
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
                f"[1:a]volume=0.06,afade=t=out:st={max(0, total_dur - 3)}:d=3[bg];"
                f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", self.audio_bitrate,
                str(final_video_path)
            ]
            subprocess.run(cmd_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            raw_stitched_video.rename(final_video_path)

        # Metadata summary
        total_seconds = sum(a["duration"] for a in turn_assets)
        file_bytes = final_video_path.stat().st_size if final_video_path.exists() else 0
        file_mb = file_bytes / (1024 * 1024)

        meta_path = self.output_dir / f"{topic_slug}_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": lesson.get("title"),
                "topic": lesson.get("topic"),
                "category": lesson.get("category"),
                "summary": lesson.get("summary"),
                "total_duration": total_seconds,
                "slides_count": total_slides,
                "video_path": str(final_video_path),
                "file_size_mb": round(file_mb, 2),
                "fps": self.fps,
                "codec": self.codec,
                "slides_dir": str(user_slides_export_dir)
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ [Completado Exitosamente] Video tutorial generado:")
        print(f"   📹 Archivo: {final_video_path}")
        print(f"   📦 Tamaño optimizado: {file_mb:.2f} MB ({file_bytes:,} bytes)")
        print(f"   ⏱️ Duración: {total_seconds:.1f} segundos (reducida ~20% gracias a {self.speech_speed}x)")
        print(f"   📂 Diapositivas HD: {user_slides_export_dir}")

        return final_video_path

    def _synthesize_host_voice(self, speaker: str, text: str, output_path: Path):
        """
        Synthesizes voice with:
        - Phonetic cleaning
        - Latin American Spanish voices (Alex: es-US / Sam: es-MX)
        - 1.2x natural speech speed via atempo=1.20 (no dead pauses)
        - Studio vocal presence & EQ
        """
        import urllib.request
        import urllib.parse

        spoken_text = clean_phonetics_for_speech(text)
        if not spoken_text:
            spoken_text = "Google Cloud Platform."

        # Latin American Spanish endpoints
        is_sam = "sam" in speaker.lower()
        lang_code = "es-MX" if is_sam else "es-US"

        # Split into natural clauses
        clauses = split_into_tts_clauses(spoken_text, max_clause_len=130)
        clause_files: List[Path] = []
        clause_dir = output_path.parent / f"_clauses_{output_path.stem}"
        clause_dir.mkdir(parents=True, exist_ok=True)

        for c_idx, clause in enumerate(clauses):
            c_file = clause_dir / f"clause_{c_idx:02d}.mp3"
            encoded_clause = urllib.parse.quote(clause)
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_clause}&tl={lang_code}&client=tw-ob"

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            try:
                with urllib.request.urlopen(req, timeout=12) as response, open(c_file, "wb") as f:
                    f.write(response.read())
                if c_file.exists() and c_file.stat().st_size > 0:
                    clause_files.append(c_file)
            except Exception as e:
                print(f"  ⚠️ Error sintetizando cláusula '{clause[:25]}...': {e}")

        # Concatenate clause audio files
        raw_concat = output_path.parent / f"_raw_concat_{output_path.name}"
        if not clause_files:
            est_dur = max(2.5, (len(text.split()) / 3.0) / self.speech_speed)
            cmd_tone = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(est_dur),
                "-acodec", "libmp3lame",
                str(output_path)
            ]
            subprocess.run(cmd_tone, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return

        if len(clause_files) == 1:
            raw_concat = clause_files[0]
        else:
            list_txt = clause_dir / "list.txt"
            with open(list_txt, "w", encoding="utf-8") as f:
                for cf in clause_files:
                    f.write(f"file '{cf.resolve()}'\n")
            cmd_cat = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_txt),
                "-c", "copy",
                str(raw_concat)
            ]
            subprocess.run(cmd_cat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Apply 1.2x tempo + Studio Vocal EQ
        tempo_filter = f"atempo={self.speech_speed:.2f}"
        if is_sam:
            dsp_af = f"{tempo_filter},highpass=f=90,equalizer=f=3000:width_type=h:width=1000:g=2.0,volume=1.25"
        else:
            dsp_af = f"{tempo_filter},highpass=f=70,bass=g=2.5:f=110:w=0.6,equalizer=f=240:width_type=h:width=80:g=1.5,volume=1.25"

        cmd_fx = [
            "ffmpeg", "-y",
            "-i", str(raw_concat),
            "-af", dsp_af,
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            str(output_path)
        ]
        subprocess.run(cmd_fx, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Cleanup temporary clause files
        try:
            for cf in clause_files:
                cf.unlink(missing_ok=True)
            (clause_dir / "list.txt").unlink(missing_ok=True)
            clause_dir.rmdir()
            if raw_concat != clause_files[0]:
                raw_concat.unlink(missing_ok=True)
        except Exception:
            pass

    def _find_ambient_soundtrack(self) -> Optional[Path]:
        """Looks for ambient lo-fi / tech audio track."""
        if MUSIC_DIR.exists():
            for ext in ("*.mp3", "*.wav", "*.m4a"):
                tracks = list(MUSIC_DIR.glob(ext))
                if tracks:
                    return tracks[0]
        return None
