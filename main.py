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
    ASSETS_DIR,
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
    sanitize_env_value,
    ENABLE_TRANSITIONS,
    DEFAULT_TRANSITION,
    TRANSITION_DURATION,
    SUPPORTED_TRANSITIONS,
    ENABLE_SFX,
    SUBTITLE_DYNAMIC,
)
from ai.script_generator import ScriptGenerator
from ai.trend_evaluator import ViralTrendEvaluator
from providers.nasa import NASAProvider
from providers.nasa_trends import NASATrendsProvider
from providers.pexels import PexelsProvider
from audio.tts import TTSManager
from audio.music import MusicManager
from audio.sfx import SFXManager
from subtitles.generator import SubtitleGenerator
from video.render import VideoRenderer
from utils.files import sanitize_filename, clean_temp_directory, check_ffmpeg, save_json, load_json


def parse_args():
    parser = argparse.ArgumentParser(
        description="🚀 Science & Stock Shorts Generator: Create automated vertical videos using NASA & Pexels media.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Topic for the video (e.g., 'agujeros negros', 'Marte'). If omitted or --trending is used, automatically hunts viral NASA discoveries."
    )
    parser.add_argument(
        "--trending", "--auto-topic",
        dest="trending",
        action="store_true",
        help="Autonomous viral topic hunter: pulls real-time NASA discoveries, ranks them with AI for viral potential, and creates the video automatically."
    )
    parser.add_argument(
        "--discover", "--list-trending",
        dest="discover",
        action="store_true",
        help="Discover mode: inspect and display available NASA trending discoveries with AI viral scores and hooks, without rendering a video."
    )
    parser.add_argument(
        "--top-choice",
        type=int,
        default=1,
        help="Which ranked viral topic to produce when using --trending (1 = highest viral score, 2 = second, etc.)"
    )
    parser.add_argument(
        "--refresh", "--refresh-trends",
        dest="refresh_trends",
        action="store_true",
        help="Force querying fresh NASA discoveries and re-evaluating with AI, bypassing cached discover results."
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
        "--prompt-file",
        type=str,
        default=None,
        help="Path to custom system prompt text file (default: loads system_prompt.txt if present, not tracked in git)"
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
    # Transition options
    parser.add_argument(
        "--transition",
        type=str,
        default=DEFAULT_TRANSITION,
        choices=SUPPORTED_TRANSITIONS,
        help=f"Visual transition between scenes (default: '{DEFAULT_TRANSITION}'; choices: {', '.join(SUPPORTED_TRANSITIONS)})"
    )
    parser.add_argument(
        "--no-transitions",
        action="store_true",
        help="Disable scene visual transitions (standard hard cuts)"
    )
    # Subtitle options
    parser.add_argument(
        "--dynamic-subtitles",
        action="store_true",
        default=SUBTITLE_DYNAMIC,
        help="Enable word-by-word active highlight subtitles (default: True)"
    )
    parser.add_argument(
        "--no-dynamic-subtitles",
        action="store_true",
        help="Disable word-by-word dynamic subtitles (use static cue lines)"
    )
    # SFX options
    parser.add_argument(
        "--sfx",
        action="store_true",
        default=ENABLE_SFX,
        help="Enable automatic synchronized sound effects (whoosh on cuts, intro boom) (default: True)"
    )
    parser.add_argument(
        "--no-sfx",
        action="store_true",
        help="Disable automatic sound effects"
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

    trending_metadata = None
    nasa_grounded_context = None

    # Auto-detect if user passed a numeric topic (e.g. --topic 2 or --topic "2" meaning option #2)
    if args.topic and args.topic.strip().isdigit() and 1 <= int(args.topic.strip()) <= 20:
        args.top_choice = int(args.topic.strip())
        args.trending = True
        args.topic = None

    # If --top-choice was explicitly passed in command line arguments, activate trending mode
    if any(arg.startswith("--top-choice") for arg in sys.argv):
        args.trending = True

    # Cache file paths: prioritize OUTPUT_DIR because in Docker containers,
    # /app/output is mounted to the host machine (e.g. -v ./output:/app/output or docker-compose)
    # ensuring discovery results persist across container restarts.
    cache_candidates = [
        OUTPUT_DIR / ".trending_cache.json",
        OUTPUT_DIR / "trending_cache.json",
        BASE_DIR / ".trending_cache.json",
    ]
    primary_cache_file = OUTPUT_DIR / ".trending_cache.json"

    # Handle Discover Mode or Autonomous Trending Discovery
    if args.discover or args.trending or not args.topic:
        print("\n" + "=" * 65)
        print("🔭 NASA VIRAL TREND HUNTER  |  Real-Time Discovery Engine")
        print("=" * 65)

        ranked_topics = None
        used_cache = False

        # Attempt to load from persistent cache if not forcing refresh
        if not args.refresh_trends:
            for c_file in cache_candidates:
                if c_file.exists():
                    cache_data = load_json(c_file)
                    if isinstance(cache_data, dict):
                        cache_lang = cache_data.get("language")
                        cache_time = cache_data.get("timestamp", 0)
                        cached_items = cache_data.get("ranked_topics", [])

                        # Cache is valid if same language, not older than 24h, and non-empty
                        if (
                            cache_lang == args.language
                            and (time.time() - cache_time < 86400)
                            and isinstance(cached_items, list)
                            and len(cached_items) > 0
                        ):
                            ranked_topics = cached_items
                            used_cache = True
                            mins_ago = int((time.time() - cache_time) / 60)
                            time_str = f"hace {mins_ago} min" if mins_ago > 0 else "hace un momento"
                            print(f"📦 Usando descubrimientos clasificados en caché ({time_str}, idioma: {args.language}).")
                            print(f"   📂 Archivo: {c_file.name} (persistente en Docker)")
                            if args.discover:
                                print("💡 (Usa '--refresh' para forzar una nueva búsqueda en vivo)")
                            break

        # If cache was not used (or forced refresh), fetch fresh from NASA and evaluate with AI
        if not ranked_topics:
            print("📡 Conectando con las APIs oficiales de la NASA (APOD & Mission Library)...")
            trends_provider = NASATrendsProvider()
            candidates = trends_provider.get_trending_candidates(limit=8)
            print(f"✅ Se obtuvieron {len(candidates)} eventos y descubrimientos científicos oficiales.")

            print("🧠 Evaluando potencial viral con IA (Curiosidad, Ganchabilidad, Espectáculo Visual)...")
            evaluator = ViralTrendEvaluator(
                gemini_key=args.gemini_key,
                openai_key=args.openai_key,
                groq_key=args.groq_key,
                preferred_provider=args.llm
            )
            ranked_topics = evaluator.evaluate_candidates(candidates, language=args.language, top_n=5)

            # Persist to cache in OUTPUT_DIR (and BASE_DIR) so subsequent container runs select the exact same items
            if ranked_topics:
                cache_time = time.time()

        # Always ensure the persistent cache in OUTPUT_DIR is written / kept in sync for Docker
        if ranked_topics:
            cache_payload = {
                "timestamp": cache_time if ('cache_time' in locals() and cache_time) else time.time(),
                "language": args.language,
                "ranked_topics": ranked_topics
            }
            save_json(cache_payload, primary_cache_file)
            try:
                save_json(cache_payload, BASE_DIR / ".trending_cache.json")
            except Exception:
                pass

        # IF DISCOVER MODE: Show rich CLI table and exit
        if args.discover:
            print("\n" + "=" * 65)
            print("🌟 DESCUBRIMIENTOS DE LA NASA CLASIFICADOS POR POTENCIAL VIRAL")
            print("=" * 65)
            for i, item in enumerate(ranked_topics):
                score = item.get("viral_score", 0.0)
                stars = "🔥" if score >= 9.0 else "⭐"
                print(f"\n[{i + 1}] {stars} Puntuación Viral: {score:.1f}/10  |  {item.get('adapted_title')}")
                print(f"    📡 Fuente:       {item.get('source')} ({item.get('date', 'Reciente')})")
                print(f"    🪝 Gancho Viral:  \"{item.get('suggested_hook')}\"")
                print(f"    💡 Razón Viral:   {item.get('viral_reason')}")
                print(f"    📖 Resumen NASA:  {item.get('scientific_summary')}")
            print("\n" + "=" * 65)
            print("💾 Lista de descubrimientos guardada en output/.trending_cache.json")
            print("   (Persistente entre contenedores Docker gracias al volumen ./output)")
            print("💡 Para generar un video de cualquier opción de la lista con total precisión:")
            print("   python main.py --trending --top-choice 1")
            print("   python main.py --trending --top-choice 2")
            print("   (En Docker: docker compose run nasa-shorts --trending --top-choice 2)")
            print("   (o usa '--refresh' para forzar una nueva consulta en vivo a la NASA)")
            print("=" * 65 + "\n")
            return

        if not ranked_topics:
            print("\n❌ No se pudieron evaluar temas de la NASA en este momento.")
            sys.exit(1)

        # IF AUTO-TRENDING: Select winning topic
        choice_idx = max(0, min(args.top_choice - 1, len(ranked_topics) - 1))
        winning = ranked_topics[choice_idx]
        trending_metadata = winning
        args.topic = winning.get("adapted_title") or winning.get("title")
        nasa_grounded_context = winning.get("scientific_text")

        # Display list of choices with clear pointer to the selected one
        if len(ranked_topics) > 1:
            print(f"\n📋 Opciones disponibles:")
            for i, it in enumerate(ranked_topics):
                mark = "👉 " if i == choice_idx else "   "
                tag = " [SELECCIONADO]" if i == choice_idx else ""
                print(f" {mark}[{i + 1}] {it.get('adapted_title')}{tag} ({it.get('viral_score', 0):.1f}/10)")

        print("\n" + "─" * 65)
        print(f"🏆 TEMA VIRAL SELECCIONADO POR IA (Opción #{choice_idx + 1} de {len(ranked_topics)}):")
        print(f"   Título:    {args.topic}")
        print(f"   Viralidad: {winning.get('viral_score', 0):.1f}/10  ({winning.get('viral_reason')})")
        print(f"   Gancho:    \"{winning.get('suggested_hook')}\"")
        if winning.get("source"):
            print(f"   Fuente:    {winning.get('source')}")
        if winning.get("credit"):
            print(f"   Crédito:   {winning.get('credit')}")
        if used_cache:
            print(f"   ℹ️  Seleccionado exactamente de la lista guardada en --discover")
            print(f"   💡 (Añade '--refresh' para forzar una nueva consulta en vivo a la NASA)")
        print("─" * 65)

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

    # 0.2 PRIORITIZED FLOW: Download real discovery media at the very beginning
    primary_asset_file = None
    primary_asset_meta = None
    if trending_metadata:
        primary_asset_file, primary_asset_meta = nasa.fetch_primary_discovery_asset(
            discovery_meta=trending_metadata,
            scene_idx=1,
            save_dir=ASSETS_DIR,
            orientation=vid_orientation
        )
        if primary_asset_meta:
            # Inform ScriptGenerator that authentic NASA media is ready for Scene 1
            p_type = primary_asset_meta.get("media_type", "visual")
            p_title = primary_asset_meta.get("title", args.topic)
            p_source = primary_asset_meta.get("source", "NASA")
            grounding_note = (
                f"\n[OFFICIAL NASA DISCOVERY VISUAL]: An authentic NASA {p_type} of '{p_title}' ({p_source}) "
                f"has been obtained and will be displayed in Scene 1. Hook the audience immediately in Scene 1 "
                f"by referencing what they are seeing in this official NASA observation."
            )
            if nasa_grounded_context:
                nasa_grounded_context += grounding_note
            else:
                nasa_grounded_context = grounding_note

    # 1. Generate Structured AI Script
    script_gen = ScriptGenerator(
        gemini_key=args.gemini_key,
        openai_key=args.openai_key,
        groq_key=args.groq_key,
        preferred_provider=args.llm,
        prompt_file=args.prompt_file
    )
    script = script_gen.generate(
        args.topic,
        target_duration=args.duration,
        language=args.language,
        context_text=nasa_grounded_context
    )

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

    # 3. Search and Download Visual Media Assets (NASA or Pexels)
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

        # Check if Scene 1 was pre-downloaded with authentic NASA discovery media
        if idx == 1 and primary_asset_file and primary_asset_file.exists() and primary_asset_meta:
            print(f"  ✅ Escena 01 asignada con el medio oficial del descubrimiento: {primary_asset_file.name}")
            print(f"     📡 Fuente / Atribución: {primary_asset_meta.get('attribution_text', 'NASA')}")
            asset_file = primary_asset_file
            meta = primary_asset_meta
        elif chosen_provider == "pexels":
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
            assets_metadata.append({
                "scene_index": idx,
                "provider": "synthetic",
                "title": f"Scene {idx}",
                "media_type": "image",
                "attribution_text": "NASA Science Archive" if is_space_topic else "Stock Visual"
            })

    # 4. Build Source Attribution Badges for Overlay
    source_attributions = []
    for timing, meta in zip(scene_timings, assets_metadata):
        if meta and meta.get("attribution_text"):
            source_attributions.append({
                "scene_id": timing.get("scene_id"),
                "start": timing.get("start", 0.0),
                "end": timing.get("end", timing.get("start", 0.0) + 5.0),
                "text": meta.get("attribution_text"),
                "is_primary": meta.get("is_primary_discovery", False)
            })

    # 5. Generate Subtitles (SRT & ASS adapted to canvas with Source Badges)
    dynamic_subs = args.dynamic_subtitles and not args.no_dynamic_subtitles
    sub_gen = SubtitleGenerator(
        width=vid_width,
        height=vid_height,
        margin_bottom=sub_margin,
        font_size=sub_font_size,
        dynamic_highlight=dynamic_subs
    )
    srt_path, ass_path = sub_gen.generate_subtitles(
        scene_timings,
        language=args.language,
        custom_font=args.font,
        source_attributions=source_attributions
    )

    # 6. Synthesize Sound Effects Track (SFX)
    sfx_enabled = args.sfx and not args.no_sfx
    sfx_track = None
    if sfx_enabled:
        sfx_mgr = SFXManager()
        sfx_track = sfx_mgr.build_sfx_timeline(scene_timings, total_duration=total_duration)

    # 6. Prepare Background Music (if available)
    music_mgr = MusicManager()
    bg_track = music_mgr.get_background_track(args.music)
    prepared_music = music_mgr.prepare_music(bg_track, target_duration=total_duration)

    # 7. Render Video Clips for Each Scene
    renderer = VideoRenderer(width=vid_width, height=vid_height, fps=VIDEO_FPS)
    print(f"\n🎞️  Rendering scene clips ({vid_width}x{vid_height} @ {VIDEO_FPS}fps)...")
    scene_clips = []
    num_scenes = len(scene_assets)
    scene_durations = [item["duration"] for item in scene_assets]

    enable_trans = not args.no_transitions and (args.transition != "none")
    trans_type = args.transition if enable_trans else "none"
    trans_duration = TRANSITION_DURATION if enable_trans else 0.0

    for i, item in enumerate(scene_assets):
        s_idx = item["scene_idx"]
        s_duration = item["duration"]
        asset_file = item["file"]
        is_video = item["is_video"]
        # Add transition padding so visual crossfades don't shorten audio sync (last scene doesn't need pad)
        pad = trans_duration if (enable_trans and i < num_scenes - 1) else 0.0

        if asset_file and asset_file.exists():
            clip = renderer.render_scene_clip(asset_file, s_duration, s_idx, is_video=is_video, transition_pad=pad)
        else:
            clip = renderer.render_emergency_color_clip(s_duration, s_idx, transition_pad=pad)
        scene_clips.append(clip)

    # 8. Assemble Final Video Output into a single folder named after the video
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
        sfx_track=sfx_track,
        assets_metadata=assets_metadata,
        output_dir=video_folder,
        language=args.language,
        scene_durations=scene_durations,
        transition=trans_type,
        transition_duration=trans_duration
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

    # 4. Sound effects track (.wav)
    sfx_dest = video_folder / "sfx.wav"
    if sfx_track and Path(sfx_track).exists():
        shutil.copy2(sfx_track, sfx_dest)

    # 5. NASA Discovery metadata if generated from trending
    nasa_dest = video_folder / "nasa_discovery.json"
    if trending_metadata:
        save_json(trending_metadata, nasa_dest)

    meta_dest = video_folder / "metadata.json"

    # 9. Clean temporary files
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
    if sfx_dest.exists():
        print(f"🔊 Efectos Sonido (.wav): {sfx_dest.resolve()}")
    if meta_dest.exists():
        print(f"📊 Metadatos (.json):   {meta_dest.resolve()}")
    print(f"⏱️  Duración Total:      {total_duration:.1f}s")
    print(f"⚡ Tiempo de Proceso:    {elapsed:.1f}s")
    print("=" * 65)


if __name__ == "__main__":
    main()
