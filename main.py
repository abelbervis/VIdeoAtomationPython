#!/usr/bin/env python3
"""
NASA & Stock Shorts Generator - Main CLI Entry Point.
Automatically creates high-retention vertical videos using NASA and Pexels media,
AI scripts, synchronized audio narration, dynamic subtitles, and FFmpeg rendering.

Usage:
  python main.py --trending
  python main.py --discover
  python main.py --topic "agujeros negros" --duration 35
  python main.py --topic "James Webb" --duration 45 --format vertical
"""

import sys
import time
import shutil
import json
from pathlib import Path

from ai.discovery import resolve_trending_topic
from ai.script_generator import ScriptGenerator
from audio.music import MusicManager
from audio.sfx import SFXManager
from audio.tts import TTSManager
from config import (
    MUSIC_VOLUME,
    PEXELS_API_KEY,
    PIXABAY_API_KEY,
    POLLINATIONS_API_KEY,
    POLLINATIONS_MODEL,
    SUPPORTED_LANGUAGES,
    TEMP_DIR,
    TRANSITION_DURATION,
    TTS_PROVIDER,
    VIDEO_FPS,
    resolve_video_format,
)
from providers.collector import collect_scene_assets, prepare_primary_discovery_asset
from providers.nasa import NASAProvider
from providers.pexels import PexelsProvider
from providers.pixabay import PixabayProvider
from providers.pollinations import PollinationsProvider
from subtitles.attribution import build_source_attributions
from subtitles.generator import SubtitleGenerator
from utils.cli import parse_args
from utils.files import check_ffmpeg, clean_temp_directory
from utils.tester import generate_audit_html, interactive_audit_menu, print_audit_console_summary
from video.deliverables import package_deliverables, print_completion_summary, resolve_video_output_folder
from video.render import VideoRenderer


def main():
    start_time = time.time()
    args = parse_args()

    # 0. Check system prerequisites
    if not check_ffmpeg():
        print("\n❌ Error: FFmpeg is required but was not found in your system PATH.")
        print("Please install FFmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)

    # 1. Resolve Topic (Autonomous NASA Trend Hunter / Discover Mode or User-Supplied Topic)
    topic, nasa_grounded_context, trending_metadata = resolve_trending_topic(args)
    args.topic = topic

    # 2. Configure Output Format & Localization Details
    fmt_cfg = resolve_video_format(args.format)
    vid_width = fmt_cfg["width"]
    vid_height = fmt_cfg["height"]
    vid_orientation = fmt_cfg["orientation"]
    sub_margin = args.subtitle_margin if args.subtitle_margin is not None else fmt_cfg["subtitle_margin_bottom"]
    sub_font_size = fmt_cfg["subtitle_font_size"]

    lang_info = SUPPORTED_LANGUAGES.get(args.language, {})
    lang_name = lang_info.get("name", args.language.upper())

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

    # 3. Initialize Media Providers
    nasa = NASAProvider()
    pexels_key = args.pexels_key or PEXELS_API_KEY
    pexels = PexelsProvider(api_key=pexels_key)
    pixabay_key = args.pixabay_key or PIXABAY_API_KEY
    pixabay = PixabayProvider(api_key=pixabay_key)
    pollinations_key = getattr(args, "pollinations_key", None) or POLLINATIONS_API_KEY
    pollinations_model = getattr(args, "pollinations_model", None) or POLLINATIONS_MODEL
    pollinations = PollinationsProvider(api_key=pollinations_key, default_model=pollinations_model)

    chosen_provider = args.provider.lower()
    if chosen_provider == "pexels" and not pexels.is_configured():
        print("\n❌ Error: PEXELS_API_KEY is required when using '--provider pexels'.")
        print("👉 You can get a free API key in 30 seconds at: https://www.pexels.com/api/")
        print("👉 Add it to your .env file: PEXELS_API_KEY=\"your_key_here\" or pass --pexels-key.\n")
        sys.exit(1)
    elif chosen_provider == "pixabay" and not pixabay.is_configured():
        print("\n❌ Error: PIXABAY_API_KEY is required when using '--provider pixabay'.")
        print("👉 You can get a free API key in 30 seconds at: https://pixabay.com/api/docs/")
        print("👉 Add it to your .env file: PIXABAY_API_KEY=\"your_key_here\" or pass --pixabay-key.\n")
        sys.exit(1)

    # 4. Download Authentic NASA Primary Discovery Asset (Scene 1) if Running Trending Topic
    primary_asset_file, primary_asset_meta, nasa_grounded_context = prepare_primary_discovery_asset(
        nasa=nasa,
        trending_metadata=trending_metadata,
        topic=args.topic,
        orientation=vid_orientation,
        nasa_grounded_context=nasa_grounded_context
    )

    # 5. Generate Structured AI Script or Load Custom Pre-edited Script
    if getattr(args, "custom_script", None):
        custom_script_path = Path(args.custom_script).expanduser().resolve()
        if not custom_script_path.exists() or not custom_script_path.is_file():
            print(f"\n❌ Error: El archivo de guion especificado no existe: {custom_script_path}")
            sys.exit(1)
        try:
            with open(custom_script_path, "r", encoding="utf-8") as f:
                script = json.load(f)
            print(f"\n📂 Cargando guion personalizado con escenas editadas desde: {custom_script_path.name}")
            if script.get("title") and not args.topic:
                args.topic = script["title"]
        except Exception as e:
            print(f"\n❌ Error al leer el archivo JSON de guion: {e}")
            sys.exit(1)
    else:
        script_gen = ScriptGenerator(
            gemini_key=args.gemini_key,
            openai_key=args.openai_key,
            groq_key=args.groq_key,
            preferred_provider=args.llm,
            prompt_file=args.prompt_file,
            enable_review=getattr(args, "review", True)
        )
        script = script_gen.generate(
            args.topic,
            target_duration=args.duration,
            language=args.language,
            context_text=nasa_grounded_context
        )

    # Strict check: If script generation fails, abort before creating media
    if not script or not script.get("scenes"):
        print("\n" + "=" * 65)
        print("❌ ERROR FATAL: No se encontraron escenas válidas en el guión.")
        print("🛑 El proceso se ha detenido por completo. No se generará audio, subtítulos ni video.")
        print("=" * 65 + "\n")
        sys.exit(1)

    scenes = script.get("scenes", [])
    print(f"📋 Script: \"{script.get('title', args.topic)}\" ({len(scenes)} scenes)")
    print(f"🪝 Hook: \"{script.get('hook', '')}\"")

    # 6. Synthesize Audio Narration & Accurate Timing
    tts_mgr = TTSManager(provider_type=TTS_PROVIDER, voice=args.voice, language=args.language)
    narration_audio, scene_timings, total_duration = tts_mgr.synthesize_script(script)

    # 7. Collect Scene Visual Media (NASA, Pexels, or Pixabay)
    scene_assets, assets_metadata = collect_scene_assets(
        scenes=scenes,
        scene_timings=scene_timings,
        topic=args.topic,
        chosen_provider=chosen_provider,
        nasa=nasa,
        pexels=pexels,
        orientation=vid_orientation,
        primary_asset_file=primary_asset_file,
        primary_asset_meta=primary_asset_meta,
        pixabay=pixabay,
        pollinations=pollinations,
        enable_ai_fallback=getattr(args, "ai_fallback", True)
    )

    # 7.5. Audit & Testing Step (Visual Storyboard & Interactive Refinement)
    video_folder, output_filename = resolve_video_output_folder(args.output, args.topic)
    audit_html_path = Path(args.audit_html) if getattr(args, "audit_html", None) else (video_folder / "storyboard_audit.html")

    # Ensure scene media assets & audio clips are immediately copied into video_folder/assets
    # so the storyboard HTML and all scene files are fully portable and permanent
    out_assets_dir = video_folder / "assets"
    out_assets_dir.mkdir(parents=True, exist_ok=True)
    for item in scene_assets:
        src_f = item.get("file")
        if src_f and Path(src_f).exists():
            dst_f = out_assets_dir / Path(src_f).name
            if dst_f.resolve() != Path(src_f).resolve():
                shutil.copy2(src_f, dst_f)
    for timing in scene_timings:
        af = timing.get("audio_file")
        if af and Path(af).exists():
            dst_a = out_assets_dir / Path(af).name
            if dst_a.resolve() != Path(af).resolve():
                shutil.copy2(af, dst_a)

    # Generate standalone interactive HTML storyboard
    generate_audit_html(
        script=script,
        scene_assets=scene_assets,
        assets_metadata=assets_metadata,
        scene_timings=scene_timings,
        topic=args.topic,
        output_html_path=audit_html_path,
        narration_audio_path=narration_audio
    )

    # Dry-Run Mode: Print audit summary and exit before rendering video
    if getattr(args, "dry_run", False):
        print_audit_console_summary(script, scene_assets, assets_metadata, scene_timings, args.topic)
        print(f"🛑 Modo Dry-Run (--dry-run) finalizado: Renderizado omitido.")
        print(f"🌐 Storyboard visual interactivo disponible en: {audit_html_path.resolve()}")
        package_deliverables(
            video_folder=video_folder,
            script=script,
            srt_path=None,
            ass_path=None,
            narration_audio=narration_audio,
            sfx_track=None,
            trending_metadata=trending_metadata,
            scene_assets=scene_assets,
            scene_timings=scene_timings
        )
        sys.exit(0)

    # Interactive Audit Mode
    if getattr(args, "audit", False):
        providers_dict = {
            "nasa": nasa,
            "pexels": pexels,
            "pixabay": pixabay,
            "pollinations": pollinations
        }
        proceed, script, scene_assets, assets_metadata, scene_timings, narration_audio = interactive_audit_menu(
            script=script,
            scene_assets=scene_assets,
            assets_metadata=assets_metadata,
            scene_timings=scene_timings,
            topic=args.topic,
            tts_mgr=tts_mgr,
            providers_dict=providers_dict,
            orientation=vid_orientation,
            html_report_path=audit_html_path,
            narration_audio=narration_audio,
            video_folder=video_folder
        )
        if not proceed:
            print(f"\n🛑 Auditoría finalizada sin renderizar.")
            print(f"📁 Recursos, guión y storyboard guardados en: {video_folder.resolve()}")
            package_deliverables(
                video_folder=video_folder,
                script=script,
                srt_path=None,
                ass_path=None,
                narration_audio=narration_audio,
                sfx_track=None,
                trending_metadata=trending_metadata,
                scene_assets=scene_assets,
                scene_timings=scene_timings
            )
            sys.exit(0)

        # Refresh scenes and total duration if scene narrations or assets were edited
        scenes = script.get("scenes", [])
        total_duration = sum(item["duration"] for item in scene_assets)

    # 8. Build Source Attribution Badges & Generate Subtitles
    source_attributions = build_source_attributions(
        scenes=scenes,
        scene_timings=scene_timings,
        assets_metadata=assets_metadata,
        language=args.language,
        topic=args.topic,
        no_badge_label=getattr(args, "no_badge_label", False),
        no_badge_date=getattr(args, "no_badge_date", False)
    )

    dynamic_subs = args.dynamic_subtitles and not args.no_dynamic_subtitles
    sub_anim = getattr(args, "subtitle_animation", "pop")
    sub_words = getattr(args, "subtitle_words", None)

    # Determine Hook Title Overlay (seconds 0-2.5 high-retention attention grabber)
    effective_hook_title = None
    if not getattr(args, "no_hook_title", False):
        if getattr(args, "hook_title", None):
            effective_hook_title = args.hook_title.strip()
        else:
            # Fall back to script title, hook, or topic
            raw_candidate = script.get("title") or script.get("hook") or args.topic
            if raw_candidate:
                words = raw_candidate.strip().split()
                effective_hook_title = " ".join(words[:7])

    sub_gen = SubtitleGenerator(
        width=vid_width,
        height=vid_height,
        margin_bottom=sub_margin,
        font_size=sub_font_size,
        dynamic_highlight=dynamic_subs,
        highlight_color=args.subtitle_color,
        animation=sub_anim
    )
    srt_path, ass_path = sub_gen.generate_subtitles(
        scene_timings,
        max_words_per_line=sub_words,
        language=args.language,
        custom_font=args.font,
        source_attributions=source_attributions,
        hook_title=effective_hook_title
    )

    # 9. Synthesize Sound Effects (SFX) & Background Music Tracks
    sfx_enabled = args.sfx and not args.no_sfx
    sfx_track = None
    if sfx_enabled:
        sfx_mgr = SFXManager(randomize=args.random_sfx)
        sfx_track = sfx_mgr.build_sfx_timeline(scene_timings, total_duration=total_duration)

    music_mgr = MusicManager()
    bg_track = music_mgr.get_background_track(args.music, shuffle=args.shuffle_music)
    m_vol = args.music_volume if args.music_volume is not None else MUSIC_VOLUME
    prepared_music = music_mgr.prepare_music(bg_track, target_duration=total_duration, volume=m_vol)

    # 10. Render Visual Scene Clips
    renderer = VideoRenderer(
        width=vid_width,
        height=vid_height,
        fps=VIDEO_FPS,
        crf=args.crf,
        preset=args.preset
    )
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

    # 11. Assemble Final Video Output
    video_folder, output_filename = resolve_video_output_folder(args.output, args.topic)

    enable_ducking = args.auto_ducking and not args.no_auto_ducking

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
        transition_duration=trans_duration,
        auto_ducking=enable_ducking
    )

    # 12. Package Deliverables inside Video Folder
    deliverables = package_deliverables(
        video_folder=video_folder,
        script=script,
        srt_path=srt_path,
        ass_path=ass_path,
        narration_audio=narration_audio,
        sfx_track=sfx_track,
        trending_metadata=trending_metadata,
        scene_assets=scene_assets,
        scene_timings=scene_timings
    )

    # 13. Clean Temporary Files
    if not args.keep_temp:
        clean_temp_directory(TEMP_DIR)

    # 14. Report Summary
    elapsed = time.time() - start_time
    print_completion_summary(
        video_folder=video_folder,
        final_video=final_video,
        deliverables=deliverables,
        total_duration=total_duration,
        elapsed_seconds=elapsed
    )


if __name__ == "__main__":
    main()
