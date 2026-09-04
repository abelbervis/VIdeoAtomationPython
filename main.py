#!/usr/bin/env python3
"""
NASA Shorts Generator - Main CLI Entry Point.
Automatically creates vertical science shorts (1080x1920 MP4) using official NASA media, AI scripts, TTS, and FFmpeg.

Usage:
  python main.py --topic "¿Qué pasaría si la Tierra dejara de girar?"
  python main.py --topic "agujeros negros" --duration 35
  python main.py --topic "Marte" --duration 30
  python main.py --topic "James Webb" --duration 45
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

from config import (
    BASE_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    DEFAULT_DURATION,
    DEFAULT_TTS_VOICE,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_language_voice,
    TTS_PROVIDER,
    MEDIA_PROVIDER,
    PEXELS_API_KEY,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    VIDEO_FPS,
    VIDEO_FORMATS,
    resolve_video_format,
    DEFAULT_VIDEO_FORMAT,
    sanitize_env_value
)
from ai.script_generator import ScriptGenerator
from providers.nasa import NASAProvider
from providers.pexels import PexelsProvider
from audio.tts import TTSManager
from audio.music import MusicManager
from subtitles.generator import SubtitleGenerator
from video.render import VideoRenderer
from utils.files import sanitize_filename, clean_temp_directory, check_ffmpeg, save_json


def parse_args():
    parser = argparse.ArgumentParser(
        description="🚀 Science & Stock Shorts Generator: Create automated vertical videos using NASA & Pexels media.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Topic for the video (e.g., 'agujeros negros', 'los secretos del océano', 'inteligencia artificial', 'Marte')"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help=f"Target duration in seconds (default: {DEFAULT_DURATION}s, range: 20-60s)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=MEDIA_PROVIDER,
        choices=["auto", "nasa", "pexels"],
        help="Media source provider:\n"
             "  'auto'   : Intelligent routing (NASA for space, Pexels for nature/tech/curiosities)\n"
             "  'nasa'   : Official NASA Image & Video Library (public domain space media)\n"
             "  'pexels' : Pexels API (high-definition vertical 9:16 stock videos & photos)"
    )
    parser.add_argument(
        "--pexels-key",
        type=str,
        default=None,
        help="Custom Pexels API key (or set PEXELS_API_KEY in .env file)"
    )
    parser.add_argument(
        "--llm",
        type=str,
        default=LLM_PROVIDER,
        choices=["auto", "groq", "gemini", "openai"],
        help="AI LLM provider to write the script:\n"
             "  'auto'   : Tries configured keys in priority order (Groq -> Gemini -> OpenAI)\n"
             "  'groq'   : Groq LPU (llama-3.3-70b-versatile, ultra-fast)\n"
             "  'gemini' : Google Gemini (gemini-2.5-flash)\n"
             "  'openai' : OpenAI (gpt-4o-mini)"
    )
    parser.add_argument(
        "--groq-key",
        type=str,
        default=None,
        help="Custom Groq API key (or set GROQ_API_KEY in .env file)"
    )
    parser.add_argument(
        "--gemini-key",
        type=str,
        default=None,
        help="Custom Google Gemini API key (or set GEMINI_API_KEY in .env file)"
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        default=None,
        help="Custom OpenAI API key (or set OPENAI_API_KEY in .env file)"
    )
    parser.add_argument(
        "--language", "--lang",
        dest="language",
        type=str,
        default=DEFAULT_LANGUAGE,
        choices=["es", "en", "zh"],
        help="Target language for narration and subtitles: 'es' (Spanish), 'en' (English), 'zh' (Chinese) (default: es)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default=DEFAULT_VIDEO_FORMAT,
        help="Video output format/aspect ratio:\n"
             "  'vertical'   : 9:16 portrait (1080x1920) - YouTube Shorts, TikTok, Reels (default)\n"
             "  'horizontal' : 16:9 landscape (1920x1080) - YouTube, standard video\n"
             "  'square'     : 1:1 square (1080x1080) - Instagram Post, LinkedIn, Facebook\n"
             "  or custom WIDTHxHEIGHT (e.g. '1280x720', '3840x2160')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output video or folder name (default: output/<video_name>/)"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=None,
        help="TTS voice model (default: auto-selected by language: es-ES-AlvaroNeural, en-US-ChristopherNeural, zh-CN-YunxiNeural)"
    )
    parser.add_argument(
        "--font",
        type=str,
        default=None,
        help="Subtitle font family (default: auto-detected, e.g. 'WenQuanYi Zen Hei' for Chinese, 'Arial' for Spanish/English)"
    )
    parser.add_argument(
        "--music",
        type=str,
        default=None,
        help="Path to custom background MP3 music file (optional)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep intermediate scene clips and audio files in temp/ directory"
    )
    return parser.parse_args()


def main():
    start_time = time.time()
    args = parse_args()

    # Sanitize inputs (strip surrounding quotes or comments if passed from shell, env, or docker)
    args.language = (args.language or DEFAULT_LANGUAGE).lower().strip()
    args.voice = get_language_voice(args.language, sanitize_env_value(args.voice) if args.voice else None)
    if args.pexels_key:
        args.pexels_key = sanitize_env_value(args.pexels_key)
    if args.groq_key:
        args.groq_key = sanitize_env_value(args.groq_key)
    if args.gemini_key:
        args.gemini_key = sanitize_env_value(args.gemini_key)
    if args.openai_key:
        args.openai_key = sanitize_env_value(args.openai_key)

    lang_info = SUPPORTED_LANGUAGES.get(args.language, {})
    lang_name = lang_info.get("name", args.language.upper())

    # Resolve video format & dimensions
    fmt_cfg = resolve_video_format(args.format)
    vid_width = fmt_cfg["width"]
    vid_height = fmt_cfg["height"]
    vid_orientation = fmt_cfg["orientation"]
    sub_margin = fmt_cfg["subtitle_margin_bottom"]
    sub_font_size = fmt_cfg["subtitle_font_size"]

    print("=" * 65)
    print("🌌  VIDEO GENERATOR  |  Multi-Format Automation Engine")
    print("=" * 65)
    print(f"🎯 Topic:        '{args.topic}'")
    print(f"📐 Format:       {fmt_cfg['description']}")
    print(f"🌍 Language:     {lang_name} ({args.language})")
    print(f"⏱️  Duration:     ~{args.duration} seconds")
    print(f"🤖 LLM Provider: {args.llm.upper()}")
    print(f"🗣️  Voice:        {args.voice}")
    print(f"🌐 Media:        {args.provider.upper()}")

    # 0. Check system prerequisites
    if not check_ffmpeg():
        print("\n❌ Error: FFmpeg is required but was not found in your system PATH.")
        print("Please install FFmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)

    # 0.1 Setup Media Providers
    nasa = NASAProvider()
    pexels_key = args.pexels_key or PEXELS_API_KEY
    pexels = PexelsProvider(api_key=pexels_key)

    chosen_provider = args.provider.lower()
    if chosen_provider == "pexels" and not pexels.is_configured():
        print("\n❌ Error: PEXELS_API_KEY is required when using '--provider pexels'.")
        print("👉 You can get a free API key in 30 seconds at: https://www.pexels.com/api/")
        print("👉 Add it to your .env file: PEXELS_API_KEY=\"your_key_here\" or pass --pexels-key.\n")
        sys.exit(1)

    # 1. Generate Structured AI Script
    script_gen = ScriptGenerator(
        gemini_key=args.gemini_key,
        openai_key=args.openai_key,
        groq_key=args.groq_key,
        preferred_provider=args.llm
    )
    script = script_gen.generate(args.topic, target_duration=args.duration, language=args.language)

    # STRICT CHECK: If script generation fails, stop immediately without proceeding to audio/video
    if not script or not script.get("scenes"):
        print("\n" + "=" * 65)
        print("❌ ERROR FATAL: La API no pudo generar el guión.")
        print("🛑 El proceso se ha detenido por completo. No se generará audio, subtítulos ni video.")
        print("=" * 65 + "\n")
        sys.exit(1)

    scenes = script.get("scenes", [])
    print(f"📋 Script generated: \"{script.get('title', args.topic)}\" ({len(scenes)} scenes)")
    print(f"🪝 Hook: \"{script.get('hook', '')}\"")

    # 2. Synthesize Audio Narration & Timing
    tts_mgr = TTSManager(provider_type=TTS_PROVIDER, voice=args.voice, language=args.language)
    narration_audio, scene_timings, total_duration = tts_mgr.synthesize_script(script)

    # 3. Generate Subtitles (SRT & ASS adapted to canvas)
    sub_gen = SubtitleGenerator(
        width=vid_width,
        height=vid_height,
        margin_bottom=sub_margin,
        font_size=sub_font_size
    )
    srt_path, ass_path = sub_gen.generate_subtitles(
        scene_timings,
        language=args.language,
        custom_font=args.font
    )

    # 4. Search and Download Visual Media Assets (NASA or Pexels)
    print(f"\n🔭 Fetching media assets (Mode: {chosen_provider.upper()})...")
    scene_assets = []
    assets_metadata = []

    # Detect if topic is space-specific for auto mode (Spanish, English, Chinese triggers)
    space_triggers = [
        # Spanish
        "tierra", "marte", "agujero", "nasa", "galaxia", "hubble", "webb", "universo",
        "planeta", "estrella", "espacio", "jupiter", "luna", "saturno", "cosmos",
        "astronauta", "sol", "solar", "orbita", "meteorito", "asteroide", "cometa", "jwst",
        # English
        "earth", "mars", "black hole", "galaxy", "universe", "planet", "star",
        "space", "jupiter", "moon", "saturn", "cosmos", "astronaut", "sun", "solar",
        "orbit", "meteor", "asteroid", "comet",
        # Chinese
        "月球", "火星", "黑洞", "宇宙", "银河", "恒星", "行星", "地球", "太空", "太阳", "韦伯", "航天"
    ]
    is_space_topic = any(t in args.topic.lower() for t in space_triggers)

    for idx, (scene, timing) in enumerate(zip(scenes, scene_timings), start=1):
        keywords = scene.get("keywords", [args.topic])
        visual_type = scene.get("visual_type", "video")
        asset_file = None
        meta = None

        if chosen_provider == "pexels":
            asset_file, meta = pexels.fetch_scene_asset(
                scene_idx=idx,
                keywords=keywords,
                preferred_type=visual_type,
                orientation=vid_orientation
            )
        elif chosen_provider == "nasa":
            asset_file, meta = nasa.fetch_scene_asset(
                scene_idx=idx,
                keywords=keywords,
                preferred_type=visual_type,
                orientation=vid_orientation
            )
        else:
            # Auto mode: route according to topic domain and available keys
            if is_space_topic or not pexels.is_configured():
                asset_file, meta = nasa.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=vid_orientation
                )
                if not asset_file and pexels.is_configured():
                    print(f"    ↳ NASA visual not found for scene {idx}, querying Pexels...")
                    asset_file, meta = pexels.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=vid_orientation
                    )
            else:
                asset_file, meta = pexels.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=vid_orientation
                )
                if not asset_file:
                    print(f"    ↳ Pexels visual not found for scene {idx}, querying NASA...")
                    asset_file, meta = nasa.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=vid_orientation
                    )

        if asset_file and meta:
            scene_assets.append({
                "scene_idx": idx,
                "file": asset_file,
                "is_video": (meta["media_type"] == "video"),
                "duration": timing["duration"]
            })
            assets_metadata.append(meta)
        else:
            print(f"  ⚠️ Using fallback background for scene {idx}...")
            scene_assets.append({
                "scene_idx": idx,
                "file": None,
                "is_video": False,
                "duration": timing["duration"]
            })

    # 5. Prepare Background Music (if available)
    music_mgr = MusicManager()
    bg_track = music_mgr.get_background_track(args.music)
    prepared_music = music_mgr.prepare_music(bg_track, target_duration=total_duration)

    # 6. Render Video Clips for Each Scene
    renderer = VideoRenderer(width=vid_width, height=vid_height, fps=VIDEO_FPS)
    print(f"\n🎞️  Rendering scene clips ({vid_width}x{vid_height} @ {VIDEO_FPS}fps)...")
    scene_clips = []

    for item in scene_assets:
        s_idx = item["scene_idx"]
        s_duration = item["duration"]
        asset_file = item["file"]
        is_video = item["is_video"]

        if asset_file and asset_file.exists():
            clip = renderer.render_scene_clip(asset_file, s_duration, s_idx, is_video=is_video)
        else:
            clip = renderer.render_emergency_color_clip(s_duration, s_idx)
        scene_clips.append(clip)

    # 7. Assemble Final Video Output into a single folder named after the video
    if args.output:
        out_candidate = Path(args.output)
        if len(out_candidate.parts) > 1:
            if out_candidate.suffix.lower() == ".mp4":
                video_name = sanitize_filename(out_candidate.stem)
                video_folder = out_candidate.parent / video_name
            else:
                video_name = sanitize_filename(out_candidate.name)
                video_folder = out_candidate
        else:
            video_name = sanitize_filename(out_candidate.stem)
            video_folder = OUTPUT_DIR / video_name
    else:
        video_name = sanitize_filename(args.topic)
        video_folder = OUTPUT_DIR / video_name

    video_name = video_name or "short_video"
    video_folder.mkdir(parents=True, exist_ok=True)
    output_filename = f"{video_name}.mp4"

    final_video = renderer.assemble_final_video(
        scene_clips=scene_clips,
        narration_audio=narration_audio,
        subtitles_file=ass_path,
        output_filename=output_filename,
        background_music=prepared_music,
        assets_metadata=assets_metadata,
        output_dir=video_folder,
        language=args.language
    )

    # Save all associated deliverables inside the single video folder
    # 1. Full AI script
    script_dest = video_folder / "script.json"
    save_json(script, script_dest)

    # 2. Synchronized Subtitles (.srt and .ass)
    srt_dest = video_folder / "subtitles.srt"
    if srt_path and Path(srt_path).exists():
        shutil.copy2(srt_path, srt_dest)

    ass_dest = video_folder / "subtitles.ass"
    if ass_path and Path(ass_path).exists():
        shutil.copy2(ass_path, ass_dest)

    # 3. Narration audio track (.mp3)
    audio_dest = video_folder / "narration.mp3"
    if narration_audio and Path(narration_audio).exists():
        shutil.copy2(narration_audio, audio_dest)

    meta_dest = video_folder / "metadata.json"

    # 8. Clean temporary files
    if not args.keep_temp:
        clean_temp_directory(TEMP_DIR)

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print("🎉 VIDEO CREATION COMPLETED SUCCESSFULLY!")
    print(f"📁 Carpeta del Video:   {video_folder.resolve()}")
    print(f"🎥 Video Final:         {final_video.resolve()}")
    print(f"📜 Guión (.json):       {script_dest.resolve()}")
    if srt_dest.exists():
        print(f"📝 Subtítulos (.srt):   {srt_dest.resolve()}")
    if audio_dest.exists():
        print(f"🎵 Narración (.mp3):    {audio_dest.resolve()}")
    if meta_dest.exists():
        print(f"📊 Metadatos (.json):   {meta_dest.resolve()}")
    print(f"⏱️  Duración Total:      {total_duration:.1f}s")
    print(f"⚡ Tiempo de Proceso:    {elapsed:.1f}s")
    print("=" * 65)


if __name__ == "__main__":
    main()
