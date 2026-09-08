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
from subtitles.attribution import build_source_attributions
from subtitles.generator import SubtitleGenerator
from utils.cli import parse_args
from utils.files import check_ffmpeg, clean_temp_directory
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

    # 5. Generate Structured AI Script
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

    # Strict check: If script generation fails, abort before creating media
    if not script or not script.get("scenes"):
        print("\n" + "=" * 65)
        print("❌ ERROR FATAL: La API no pudo generar el guión.")
        print("🛑 El proceso se ha detenido por completo. No se generará audio, subtítulos ni video.")
        print("=" * 65 + "\n")
        sys.exit(1)

    scenes = script.get("scenes", [])
    print(f"📋 Script generated: \"{script.get('title', args.topic)}\" ({len(scenes)} scenes)")
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
        pixabay=pixabay
    )

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
    sub_gen = SubtitleGenerator(
        width=vid_width,
        height=vid_height,
        margin_bottom=sub_margin,
        font_size=sub_font_size,
        dynamic_highlight=dynamic_subs,
        highlight_color=args.subtitle_color
    )
    srt_path, ass_path = sub_gen.generate_subtitles(
        scene_timings,
        language=args.language,
        custom_font=args.font,
        source_attributions=source_attributions
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

    # 12. Package Deliverables inside Video Folder
    deliverables = package_deliverables(
        video_folder=video_folder,
        script=script,
        srt_path=srt_path,
        ass_path=ass_path,
        narration_audio=narration_audio,
        sfx_track=sfx_track,
        trending_metadata=trending_metadata
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
