"""
GCP Tutorial & Console Simulator Video Builder - Flagship Edition.
Features:
- Authentic Mexican Male Narrator ('es-MX-JorgeNeural' via edge-tts at calibrated +8% pace).
- Direct, Practical Hook & Storytelling (no boring theory or fake synthetic debates).
- Hyper-Realistic Google Cloud Console UI Simulation:
  * Alerta de factura real vs solución Cloud Storage
  * Creación interactiva de bucket en GCP Console
  * Las 4 metáforas cotidianas (Cajón, Armario, Bodega, Caja fuerte) con resaltado secuencial dinámico
  * Drag & Drop de archivos con cifrado bancario automático
  * Zoom enfocado a comandos de gcloud storage CLI con diálogo fluido
  * Reglas de oro para ahorrar el 80%
- Extreme File Size & Bitrate Optimization:
  * 15 FPS
  * -tune stillimage with CRF 26
  * 96 kbps AAC audio
  * Zero Ken Burns / 100% vector sharpness
  * Subtítulos flotantes sin superposición (y=h-96)
"""

import asyncio
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
from video.gcp_console_renderer import GCPConsoleRenderer
from video.visual_resource_router import VisualResourceRouter


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
    """Builds hands-on audiovisual tutorials with GCP Console simulation and JorgeNeural Mexican male narrator."""

    def __init__(
        self,
        output_dir: Path = OUTPUT_DIR / "gcp_tutorials",
        temp_dir: Path = TEMP_DIR / "gcp_build",
        width: int = 1920,
        height: int = 1080,
        burn_subtitles: bool = True,
        enable_music: bool = True,
        speech_speed: float = 1.08,
        fps: int = 15,
        crf: int = 26,
        codec: str = "libx264",
        audio_bitrate: str = "96k",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        llm_provider: str = "auto",
        strict_mode: bool = False,
        single_voice: bool = True
    ):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.width = width
        self.height = height
        self.burn_subtitles = burn_subtitles
        self.enable_music = enable_music
        self.speech_speed = max(1.0, min(1.3, speech_speed))
        self.fps = fps
        self.crf = crf
        self.codec = codec if codec in ("libx265", "libx264") else "libx264"
        self.audio_bitrate = audio_bitrate
        self.gemini_key = gemini_key
        self.groq_key = groq_key
        self.llm_provider = llm_provider
        self.strict_mode = strict_mode
        self.single_voice = single_voice
        self.slide_renderer = GCPSlideRenderer(width, height)
        self.console_renderer = GCPConsoleRenderer(width, height)
        self.router = VisualResourceRouter()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def build_tutorial_video(
        self,
        lesson: Dict[str, Any],
        output_file_name: Optional[str] = None,
        force_hybrid: bool = False,
        single_voice: Optional[bool] = None
    ) -> Path:
        """Dispatches to hybrid multi-resource router, console tutorial simulation, or classic slide builder."""
        if single_voice is not None:
            self.single_voice = single_voice
        if force_hybrid or lesson.get("mode") == "hybrid" or lesson.get("hybrid_timeline"):
            return self._build_hybrid_timeline_video(lesson, output_file_name)
        elif lesson.get("mode") == "console_tutorial" or "scenes" in lesson:
            return self._build_console_tutorial_video(lesson, output_file_name)
        else:
            return self._build_classic_slide_video(lesson, output_file_name)

    def _build_hybrid_timeline_video(
        self,
        lesson: Dict[str, Any],
        output_file_name: Optional[str] = None
    ) -> Path:
        """
        Builds a multi-resource video where each scene alternates between:
        - Slide (vector infographic with sequential highlight)
        - AI Motion Clip (RAG-powered vector animation loop)
        - Console (simulated GCP Console walkthrough)
        - Terminal (live CLI command execution)
        """
        topic_slug = lesson.get("topic", "gcp_hybrid").lower().replace(" ", "_")
        topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "_")[:32]
        target_name = output_file_name or f"tutorial_hybrid_{topic_slug}.mp4"
        final_video_path = self.output_dir / target_name

        timeline = self.router.plan_hybrid_timeline(lesson)
        total_scenes = len(timeline)

        # Count resource distribution
        counts: Dict[str, int] = {}
        for item in timeline:
            k = item.get("resource_kind", "slide")
            counts[k] = counts.get(k, 0) + 1

        dist_str = ", ".join(f"{count} {kind.upper()}" for kind, count in counts.items())
        print(f"\n🎬 [Orquestador de Recursos Visuales • Router Semántico]")
        print(f"   • Título: '{lesson.get('title')}'")
        print(f"   • Línea de Tiempo Multi-Recurso: {total_scenes} escenas")
        print(f"   • Distribución Asignada: {dist_str}")
        print(f"   • Locutor: es-MX-JorgeNeural (+8% ritmo ágil)")

        audio_dir = self.temp_dir / "audio"
        slides_cache_dir = self.temp_dir / "slides"
        segments_dir = self.temp_dir / "segments"
        subs_dir = self.temp_dir / "subtitles"
        motion_cache_dir = self.temp_dir / "motion_cache"

        audio_dir.mkdir(parents=True, exist_ok=True)
        slides_cache_dir.mkdir(parents=True, exist_ok=True)
        segments_dir.mkdir(parents=True, exist_ok=True)
        subs_dir.mkdir(parents=True, exist_ok=True)
        motion_cache_dir.mkdir(parents=True, exist_ok=True)

        user_assets_export_dir = self.output_dir / f"{topic_slug}_hybrid_scenes"
        user_assets_export_dir.mkdir(parents=True, exist_ok=True)

        # Lazy load AIMotionGenerator
        from video.ai_motion_generator import AIMotionGenerator
        motion_gen = AIMotionGenerator(
            width=self.width,
            height=self.height,
            fps=self.fps,
            crf=self.crf,
            temp_dir=self.temp_dir / "motion_tmp",
            output_dir=motion_cache_dir,
            gemini_key=self.gemini_key,
            groq_key=self.groq_key,
            llm_provider=self.llm_provider,
            strict_mode=self.strict_mode
        )

        segment_assets = []
        font_param, _ = resolve_best_font_path()

        for idx, item in enumerate(timeline, start=1):
            kind = item.get("resource_kind", "slide")
            r_id = item.get("resource_id", "default")
            dialogue_text = item.get("dialogue", "")
            slide_data = item.get("slide_data", {})
            speaker = item.get("speaker", "Alex")

            # 1. Synthesize neural audio with speaker personality
            audio_path = audio_dir / f"turn_{idx:02d}.mp3"
            self._synthesize_voice(dialogue_text, audio_path, speaker=speaker)
            duration = max(get_media_duration(audio_path), 2.5)

            # 2. Render visual asset based on resource_kind
            visual_video_clip: Optional[Path] = None
            visual_img_path: Optional[Path] = None

            if kind == "motion":
                motion_topic = item.get("title") or lesson.get("topic") or "GCP Concept"
                try:
                    clip_path, _ = motion_gen.generate_motion_for_topic(
                        topic=motion_topic,
                        user_notes=dialogue_text,
                        output_filename=f"clip_seg_{idx:02d}.mp4"
                    )
                    if clip_path.exists() and clip_path.stat().st_size > 0:
                        visual_video_clip = clip_path
                except Exception as e:
                    print(f"   ⚠️ Fallback a diapositiva para escena {idx} ({e})")
                    kind = "slide"

            if kind == "console":
                console_svg = self.console_renderer.render_console_scene_svg(
                    scene_type=item.get("scene_data", {}).get("scene_type", "storage_analogies"),
                    title=item.get("title", "Google Cloud Console"),
                    highlight_keyword=item.get("scene_data", {}).get("keyword", ""),
                    extra_data={"active_index": idx % 4}
                )
                visual_img_path = slides_cache_dir / f"console_{idx:02d}.png"
                self.console_renderer.rasterize_svg_to_png(console_svg, visual_img_path)

            if kind == "slide" or (not visual_video_clip and not visual_img_path):
                slide_data_to_use = slide_data or {
                    "layout": "concept_card",
                    "title": item.get("title", lesson.get("title", "Concepto")),
                    "subtitle": lesson.get("summary", ""),
                    "badge": "PUNTO CLAVE",
                    "concept_title": item.get("title", "Google Cloud Architecture"),
                    "bullet_points": [dialogue_text[:120]]
                }
                slide_svg = self.slide_renderer.render_slide_svg(
                    slide=slide_data_to_use,
                    active_speaker=speaker if not self.single_voice else "Instructor",
                    current_slide_num=idx,
                    total_slides=total_scenes,
                    series_category=lesson.get("category", "Google Cloud Architecture"),
                    focus_index=idx % 3,
                    single_voice=self.single_voice
                )
                visual_img_path = slides_cache_dir / f"slide_{idx:02d}.png"
                self.slide_renderer.rasterize_svg_to_png(slide_svg, visual_img_path)

            segment_assets.append({
                "index": idx,
                "kind": kind,
                "r_id": r_id,
                "text": dialogue_text,
                "duration": duration,
                "audio_path": audio_path,
                "video_clip": visual_video_clip,
                "img_path": visual_img_path
            })

        # 3. Encode segments
        segment_files = []
        for asset in segment_assets:
            idx = asset["index"]
            dur = asset["duration"]
            aud = asset["audio_path"]
            seg_out = segments_dir / f"segment_{idx:02d}.mp4"

            # Discrete subtitle filter
            subtitle_filter = ""
            if self.burn_subtitles:
                sub_file = subs_dir / f"caption_{idx:02d}.txt"
                wrapped = wrap_text_for_subtitles(asset["text"], max_chars_per_line=85)
                sub_file.write_text(wrapped, encoding="utf-8")
                escaped_sub_path = str(sub_file.resolve()).replace("\\", "/").replace(":", "\\:")
                subtitle_filter = (
                    f",drawtext={font_param}:textfile='{escaped_sub_path}':"
                    f"fontcolor=white:fontsize=17:line_spacing=4:box=1:boxcolor=0x000000@0.75:boxborderw=8:"
                    f"x=(w-text_w)/2:y=h-96"
                )

            vf_string = f"scale={self.width}:{self.height},format=yuv420p{subtitle_filter}"

            if asset["video_clip"] and asset["video_clip"].exists():
                cmd = [
                    "ffmpeg", "-y",
                    "-stream_loop", "-1",
                    "-t", f"{dur:.2f}",
                    "-i", str(asset["video_clip"]),
                    "-i", str(aud),
                    "-vf", vf_string,
                    "-r", str(self.fps),
                    "-c:v", self.codec,
                    "-preset", "veryfast",
                    "-crf", str(self.crf),
                    "-c:a", "aac",
                    "-b:a", self.audio_bitrate,
                    "-shortest",
                    str(seg_out)
                ]
            else:
                img = asset["img_path"]
                if not img.exists() or img.stat().st_size == 0:
                    cmd_fb = [
                        "ffmpeg", "-y",
                        "-f", "lavfi",
                        "-i", f"color=c=0x0B0F19:s={self.width}x{self.height}:d=1",
                        "-vframes", "1",
                        str(img)
                    ]
                    subprocess.run(cmd_fb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            segment_files.append(seg_out)

        # 4. Concatenate segments
        concat_list_file = self.temp_dir / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for s in segment_files:
                f.write(f"file '{s.resolve()}'\n")

        raw_stitched = self.temp_dir / "raw_stitched.mp4"
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_file), "-c", "copy", str(raw_stitched)], check=True)

        # 5. Background soundtrack
        bg_music = self._find_ambient_soundtrack()
        total_seconds = sum(a["duration"] for a in segment_assets)
        if self.enable_music and bg_music and bg_music.exists():
            cmd_mix = [
                "ffmpeg", "-y",
                "-i", str(raw_stitched),
                "-stream_loop", "-1",
                "-i", str(bg_music),
                "-filter_complex",
                f"[1:a]volume=0.04,afade=t=out:st={max(0, total_seconds - 3)}:d=3[bg];"
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
            raw_stitched.rename(final_video_path)

        file_bytes = final_video_path.stat().st_size if final_video_path.exists() else 0
        file_mb = file_bytes / (1024 * 1024)

        meta_path = self.output_dir / f"{topic_slug}_hybrid_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": lesson.get("title"),
                "topic": lesson.get("topic"),
                "mode": "hybrid_multi_resource",
                "narrator": "es-MX-JorgeNeural (Hombre Mexicano)",
                "total_duration": total_seconds,
                "scenes_count": total_scenes,
                "resource_distribution": counts,
                "video_path": str(final_video_path),
                "file_size_mb": round(file_mb, 2),
                "fps": self.fps,
                "codec": self.codec
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ [Completado Exitosamente] Video tutorial HÍBRIDO generado:")
        print(f"   📹 Archivo: {final_video_path}")
        print(f"   📦 Tamaño: {file_mb:.2f} MB ({file_bytes:,} bytes)")
        print(f"   ⏱️ Duración: {total_seconds:.1f} segundos (~{round(total_seconds / 60, 1)} minutos)")
        print(f"   🎭 Recursos combinados: {dist_str}")

        return final_video_path

    def _build_console_tutorial_video(
        self,
        lesson: Dict[str, Any],
        output_file_name: Optional[str] = None
    ) -> Path:
        """
        Builds dynamic Google Cloud Console hands-on walkthrough:
        - Real Console UI scenes with sequential active focus
        - Neural Mexican male voice (es-MX-JorgeNeural at +8%)
        - Direct to the point (~1.5 minutes)
        - 15 FPS, CRF 26, AAC 96k
        """
        topic_slug = lesson.get("topic", "gcp_storage").lower().replace(" ", "_")
        topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "_")[:32]
        
        target_name = output_file_name or f"tutorial_{topic_slug}.mp4"
        final_video_path = self.output_dir / target_name

        scenes = lesson.get("scenes", [])
        total_scenes = len(scenes)

        print(f"\n🚀 [GCP Console Simulator Video Builder]")
        print(f"   • Título: '{lesson.get('title')}'")
        print(f"   • Formato: Simulación Visual de Google Cloud Console + Metáforas Cotidianas")
        print(f"   • Locutor: es-MX-JorgeNeural (Voz masculina mexicana neural a +8%)")
        print(f"   • Escenas prácticas: {total_scenes}")
        print(f"   • Optimización: {self.width}x{self.height} @ {self.fps} FPS ({self.codec}, CRF {self.crf})")

        audio_dir = self.temp_dir / "audio"
        scenes_dir = self.temp_dir / "scenes"
        segments_dir = self.temp_dir / "segments"
        subs_dir = self.temp_dir / "subtitles"

        audio_dir.mkdir(parents=True, exist_ok=True)
        scenes_dir.mkdir(parents=True, exist_ok=True)
        segments_dir.mkdir(parents=True, exist_ok=True)
        subs_dir.mkdir(parents=True, exist_ok=True)

        user_scenes_export_dir = self.output_dir / f"{topic_slug}_scenes"
        user_scenes_export_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Render scenes and synthesize Mexican male voice
        print(f"\n🎙️ [Audio & Consola] Sintetizando voz masculina mexicana y renderizando interfaz...")
        scene_assets: List[Dict[str, Any]] = []

        for idx, scene in enumerate(scenes, start=1):
            s_type = scene.get("scene_type", "storage_analogies")
            s_title = scene.get("title", "Google Cloud Storage")
            s_keyword = scene.get("keyword", "")
            dialogue_text = scene.get("dialogue", "")
            
            extra_data = {}
            if "active_index" in scene:
                extra_data["active_index"] = scene["active_index"]

            # 1. Render Console Scene SVG to PNG
            scene_svg = self.console_renderer.render_console_scene_svg(
                scene_type=s_type,
                title=s_title,
                highlight_keyword=s_keyword,
                extra_data=extra_data
            )
            scene_img = scenes_dir / f"scene_{idx:02d}_{s_type}.png"
            self.console_renderer.rasterize_svg_to_png(scene_svg, scene_img)

            # Export standalone high-res image
            export_png = user_scenes_export_dir / f"scene_{idx:02d}_{s_type}.png"
            self.console_renderer.rasterize_svg_to_png(scene_svg, export_png)

            # 2. Synthesize authentic Mexican male voice
            audio_path = audio_dir / f"scene_audio_{idx:02d}.mp3"
            self._synthesize_mexican_male_voice(dialogue_text, audio_path)

            duration = get_media_duration(audio_path)
            duration = max(duration, 3.0)

            scene_assets.append({
                "scene_id": idx,
                "title": s_title,
                "keyword": s_keyword,
                "text": dialogue_text,
                "img": scene_img,
                "audio": audio_path,
                "duration": duration
            })

            clean_preview = clean_phonetics_for_speech(dialogue_text)[:45]
            print(f"   • [Escena {idx:02d} | {s_keyword}] {duration:.1f}s — \"{clean_preview}...\"")

        # Step 2: Render video segments at 15 FPS with stillimage tuning
        print(f"\n🎬 [FFmpeg Encoding] Codificando escenas de consola a {self.fps} FPS...")
        segment_files: List[Path] = []
        font_param, _ = resolve_best_font_path()

        for asset in scene_assets:
            idx = asset["scene_id"]
            dur = asset["duration"]
            img = asset["img"]
            aud = asset["audio"]
            seg_out = segments_dir / f"segment_{idx:02d}.mp4"

            # Fallback check
            if not img.exists() or img.stat().st_size == 0:
                cmd_fb = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=0x0B0F19:s={self.width}x{self.height}:d=1",
                    "-vframes", "1",
                    str(img)
                ]
                subprocess.run(cmd_fb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Sleek, compact bottom caption positioned at y=h-96 to avoid bottom bar overlap
            subtitle_filter = ""
            if self.burn_subtitles:
                sub_file = subs_dir / f"caption_{idx:02d}.txt"
                wrapped = wrap_text_for_subtitles(asset["text"], max_chars_per_line=85)
                sub_file.write_text(wrapped, encoding="utf-8")
                escaped_sub_path = str(sub_file.resolve()).replace("\\", "/").replace(":", "\\:")
                
                subtitle_filter = (
                    f",drawtext={font_param}:textfile='{escaped_sub_path}':"
                    f"fontcolor=white:fontsize=17:line_spacing=4:box=1:boxcolor=0x000000@0.75:boxborderw=8:"
                    f"x=(w-text_w)/2:y=h-96"
                )

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

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            segment_files.append(seg_out)

        # Step 3: Concat all segments into master tutorial
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
            print(f"   🎶 Añadiendo música ambiental: {bg_music.name}")
            total_dur = sum(a["duration"] for a in scene_assets)
            cmd_mix = [
                "ffmpeg", "-y",
                "-i", str(raw_stitched_video),
                "-stream_loop", "-1",
                "-i", str(bg_music),
                "-filter_complex",
                f"[1:a]volume=0.04,afade=t=out:st={max(0, total_dur - 3)}:d=3[bg];"
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

        total_seconds = sum(a["duration"] for a in scene_assets)
        file_bytes = final_video_path.stat().st_size if final_video_path.exists() else 0
        file_mb = file_bytes / (1024 * 1024)

        meta_path = self.output_dir / f"{topic_slug}_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": lesson.get("title"),
                "topic": lesson.get("topic"),
                "category": lesson.get("category"),
                "summary": lesson.get("summary"),
                "narrator": "es-MX-JorgeNeural (Hombre Mexicano)",
                "total_duration": total_seconds,
                "scenes_count": total_scenes,
                "video_path": str(final_video_path),
                "file_size_mb": round(file_mb, 2),
                "fps": self.fps,
                "codec": self.codec,
                "scenes_dir": str(user_scenes_export_dir)
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ [Completado Exitosamente] Video tutorial didáctico generado:")
        print(f"   📹 Archivo: {final_video_path}")
        print(f"   📦 Tamaño: {file_mb:.2f} MB ({file_bytes:,} bytes)")
        print(f"   ⏱️ Duración: {total_seconds:.1f} segundos (~{round(total_seconds / 60, 1)} minutos)")
        print(f"   📂 Escenas HD: {user_scenes_export_dir}")

        return final_video_path

    def _build_classic_slide_video(
        self,
        lesson: Dict[str, Any],
        output_file_name: Optional[str] = None
    ) -> Path:
        """Fallback for classic slide-based lessons."""
        topic_slug = lesson.get("topic", "gcp_tutorial").lower().replace(" ", "_")
        topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "_")[:32]
        target_name = output_file_name or f"tutorial_{topic_slug}.mp4"
        final_video_path = self.output_dir / target_name

        slides_dict = {}
        slides_list = lesson.get("slides", [])
        for s_idx, s in enumerate(slides_list, start=1):
            if isinstance(s, dict):
                s_id = s.get("slide_id") or s.get("id") or s.get("slide_number") or s.get("number") or s_idx
                try:
                    s_id = int(s_id)
                except (ValueError, TypeError):
                    s_id = s_idx
                s["slide_id"] = s_id
                slides_dict[s_id] = s

        dialogue_turns = lesson.get("dialogue", [])
        total_slides = max(len(slides_dict), 1)

        audio_dir = self.temp_dir / "audio"
        slides_cache_dir = self.temp_dir / "slides"
        segments_dir = self.temp_dir / "segments"
        subs_dir = self.temp_dir / "subtitles"

        audio_dir.mkdir(parents=True, exist_ok=True)
        slides_cache_dir.mkdir(parents=True, exist_ok=True)
        segments_dir.mkdir(parents=True, exist_ok=True)
        subs_dir.mkdir(parents=True, exist_ok=True)

        user_slides_export_dir = self.output_dir / f"{topic_slug}_slides"
        user_slides_export_dir.mkdir(parents=True, exist_ok=True)

        for s_id, s_data in slides_dict.items():
            svg_standalone = self.slide_renderer.render_slide_svg(
                slide=s_data,
                active_speaker="Alex" if not self.single_voice else "Instructor",
                current_slide_num=int(s_id),
                total_slides=total_slides,
                series_category=lesson.get("category", "Google Cloud Architecture"),
                single_voice=self.single_voice
            )
            export_png = user_slides_export_dir / f"slide_{int(s_id):02d}.png"
            self.slide_renderer.rasterize_svg_to_png(svg_standalone, export_png)

        turn_assets = []
        # Calculate turn counts per slide to sequence focus dynamically across turns
        slide_turn_counts: Dict[int, int] = {}
        for turn in dialogue_turns:
            s_id = turn.get("slide_id", 1)
            slide_turn_counts[s_id] = slide_turn_counts.get(s_id, 0) + 1

        slide_turn_tracker: Dict[int, int] = {}

        for idx, turn in enumerate(dialogue_turns, start=1):
            slide_id = turn.get("slide_id", 1)
            dialogue_text = turn.get("text", "")
            speaker = turn.get("speaker", "Alex")
            slide_data = slides_dict.get(slide_id, list(slides_dict.values())[0])

            turn_on_slide = slide_turn_tracker.get(slide_id, 0)
            slide_turn_tracker[slide_id] = turn_on_slide + 1
            turns_for_slide = slide_turn_counts.get(slide_id, 1)

            # Sequential highlighting logic based on slide layout
            layout = slide_data.get("layout", "concept_card")
            focus_idx: Optional[int] = None
            show_exec: bool = False

            if layout == "comparison_table":
                rows_count = len(slide_data.get("rows", []))
                if rows_count > 0:
                    focus_idx = turn_on_slide % rows_count
            elif layout == "architecture_flow":
                steps_count = len(slide_data.get("steps", []))
                if steps_count > 0:
                    focus_idx = turn_on_slide % steps_count
            elif layout == "concept_card":
                bullets_count = len(slide_data.get("bullet_points", []))
                if bullets_count > 0:
                    focus_idx = min(turn_on_slide, bullets_count)
            elif layout == "terminal_code":
                show_exec = (turn_on_slide > 0 or turns_for_slide == 1)
            elif layout == "hierarchy_tree":
                nodes_count = len(slide_data.get("nodes", []))
                if nodes_count > 0:
                    focus_idx = turn_on_slide % nodes_count

            audio_path = audio_dir / f"turn_{idx:02d}.mp3"
            self._synthesize_voice(dialogue_text, audio_path, speaker=speaker)

            duration = max(get_media_duration(audio_path), 2.5)

            slide_svg = self.slide_renderer.render_slide_svg(
                slide=slide_data,
                active_speaker=speaker if not self.single_voice else "Instructor",
                current_slide_num=slide_id,
                total_slides=total_slides,
                series_category=lesson.get("category", "Google Cloud Architecture"),
                focus_index=focus_idx,
                show_execution=show_exec,
                single_voice=self.single_voice
            )
            slide_img_path = slides_cache_dir / f"frame_{idx:02d}.png"
            self.slide_renderer.rasterize_svg_to_png(slide_svg, slide_img_path)

            turn_assets.append({
                "turn_id": idx,
                "text": dialogue_text,
                "speaker": speaker,
                "audio_path": audio_path,
                "slide_img": slide_img_path,
                "duration": duration
            })

        segment_files = []
        font_param, _ = resolve_best_font_path()

        for asset in turn_assets:
            idx = asset["turn_id"]
            dur = asset["duration"]
            img = asset["slide_img"]
            aud = asset["audio_path"]
            seg_out = segments_dir / f"segment_{idx:02d}.mp4"

            # Guaranteed image fallback if rasterization had an issue
            if not img.exists() or img.stat().st_size == 0:
                cmd_fb = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=0x0B0F19:s={self.width}x{self.height}:d=1",
                    "-vframes", "1",
                    str(img)
                ]
                subprocess.run(cmd_fb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            subtitle_filter = ""
            if self.burn_subtitles:
                sub_file = subs_dir / f"caption_{idx:02d}.txt"
                wrapped = wrap_text_for_subtitles(asset["text"], max_chars_per_line=85)
                sub_file.write_text(wrapped, encoding="utf-8")
                escaped_sub_path = str(sub_file.resolve()).replace("\\", "/").replace(":", "\\:")
                subtitle_filter = (
                    f",drawtext={font_param}:textfile='{escaped_sub_path}':"
                    f"fontcolor=white:fontsize=17:line_spacing=4:box=1:boxcolor=0x000000@0.75:boxborderw=8:"
                    f"x=(w-text_w)/2:y=h-96"
                )

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
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            segment_files.append(seg_out)

        concat_list_file = self.temp_dir / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for s in segment_files:
                f.write(f"file '{s.resolve()}'\n")

        raw_stitched = self.temp_dir / "raw_stitched.mp4"
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_file), "-c", "copy", str(raw_stitched)], check=True)

        # Ambient soundtrack mixing
        bg_music = self._find_ambient_soundtrack()
        if self.enable_music and bg_music and bg_music.exists():
            print(f"   🎶 Añadiendo música ambiental: {bg_music.name}")
            total_dur = sum(a["duration"] for a in turn_assets)
            cmd_mix = [
                "ffmpeg", "-y",
                "-i", str(raw_stitched),
                "-stream_loop", "-1",
                "-i", str(bg_music),
                "-filter_complex",
                f"[1:a]volume=0.04,afade=t=out:st={max(0, total_dur - 3)}:d=3[bg];"
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
            raw_stitched.rename(final_video_path)

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
                "narrator": "es-MX-JorgeNeural (Hombre Mexicano)",
                "total_duration": total_seconds,
                "turns_count": len(turn_assets),
                "slides_count": total_slides,
                "video_path": str(final_video_path),
                "file_size_mb": round(file_mb, 2),
                "fps": self.fps,
                "codec": self.codec,
                "slides_dir": str(user_slides_export_dir)
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ [Completado Exitosamente] Video tutorial generado:")
        print(f"   📹 Archivo: {final_video_path}")
        print(f"   📦 Tamaño: {file_mb:.2f} MB ({file_bytes:,} bytes)")
        print(f"   ⏱️ Duración: {total_seconds:.1f} segundos (~{round(total_seconds / 60, 1)} minutos)")
        print(f"   📂 Diapositivas HD: {user_slides_export_dir}")

        return final_video_path

    def _synthesize_voice(self, text: str, output_path: Path, speaker: str = "Alex"):
        """
        Synthesizes speech with distinct character profiles:
        - Alex / Single Instructor: Deep, resonant Mexican male architect voice (es-MX, lower pitch, bass presence)
        - Sam (DevOps): Brisk, higher-pitched, bright DevOps engineer voice (es-ES, treble clarity, dynamic cadence)
        - Single Voice mode: All turns are voiced by Lead Instructor.
        """
        spoken_text = clean_phonetics_for_speech(text)
        if not spoken_text:
            spoken_text = "Google Cloud Platform."

        is_sam = ("sam" in (speaker or "").lower()) and not self.single_voice

        # 1. Try edge-tts if installed
        try:
            import edge_tts
            rate_pct = f"+{int((self.speech_speed - 1.0) * 100)}%" if self.speech_speed >= 1.0 else f"{int((self.speech_speed - 1.0) * 100)}%"
            if rate_pct == "+0%":
                rate_pct = "+8%"
            edge_voice = "es-ES-ElviraNeural" if is_sam else "es-MX-JorgeNeural"

            async def _run_edge():
                comm = edge_tts.Communicate(
                    text=spoken_text,
                    voice=edge_voice,
                    rate=rate_pct
                )
                await comm.save(str(output_path))

            asyncio.run(_run_edge())
            if output_path.exists() and output_path.stat().st_size > 1000:
                return
        except Exception:
            pass

        # 2. Resilient Google Translate TTS with Character DSP Formant Transformation
        import urllib.request
        import urllib.parse

        clauses = split_into_tts_clauses(spoken_text, max_clause_len=110)
        clause_files: List[Path] = []
        clause_dir = output_path.parent / f"_clauses_{output_path.stem}"
        clause_dir.mkdir(parents=True, exist_ok=True)

        tl_code = "es-ES" if is_sam else "es-MX"

        for c_idx, clause in enumerate(clauses):
            c_file = clause_dir / f"clause_{c_idx:02d}.mp3"
            encoded_clause = urllib.parse.quote(clause)
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_clause}&tl={tl_code}&client=tw-ob"

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
                print(f"  ⚠️ Error en locución para cláusula '{clause[:25]}...': {e}")

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

        # Apply distinct DSP character profile
        if is_sam:
            # Sam: Distinct bright DevOps voice (+2.5 semitones higher, clear mid-treble)
            tempo_compensation = self.speech_speed / 1.15
            dsp_af = (
                f"asetrate=44100*1.15,aresample=44100,"
                f"atempo={tempo_compensation:.3f},"
                f"highpass=f=120,"
                f"equalizer=f=1500:width_type=h:width=400:g=2.5,"
                f"treble=g=3.0:f=3500,"
                f"volume=1.25"
            )
        else:
            # Alex / Single Instructor: Deep, resonant Mexican male architect voice
            tempo_compensation = self.speech_speed / 0.84
            dsp_af = (
                f"asetrate=44100*0.84,aresample=44100,"
                f"atempo={tempo_compensation:.3f},"
                f"bass=g=4.0:f=120:w=0.6,"
                f"equalizer=f=200:width_type=h:width=100:g=2.5,"
                f"treble=g=1.5:f=3500,"
                f"volume=1.30"
            )

        cmd_fx = [
            "ffmpeg", "-y",
            "-i", str(raw_concat),
            "-af", dsp_af,
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            str(output_path)
        ]
        subprocess.run(cmd_fx, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        try:
            for cf in clause_files:
                cf.unlink(missing_ok=True)
            (clause_dir / "list.txt").unlink(missing_ok=True)
            clause_dir.rmdir()
            if raw_concat != clause_files[0]:
                raw_concat.unlink(missing_ok=True)
        except Exception:
            pass

    def _synthesize_mexican_male_voice(self, text: str, output_path: Path):
        """Compatibility wrapper for legacy calls."""
        return self._synthesize_voice(text, output_path, speaker="Alex")

    def _find_ambient_soundtrack(self) -> Optional[Path]:
        """Looks for ambient lo-fi / tech audio track."""
        if MUSIC_DIR.exists():
            for ext in ("*.mp3", "*.wav", "*.m4a"):
                tracks = list(MUSIC_DIR.glob(ext))
                if tracks:
                    return tracks[0]
        return None
