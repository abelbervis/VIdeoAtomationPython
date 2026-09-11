"""
Command-Line Interface (CLI) Parser for Science & Stock Shorts Generator.
Defines all CLI flags, descriptions, defaults, and input sanitization.
"""

import argparse
import sys
from typing import Any

from config import (
    CURATED_SUBTITLE_COLORS,
    DEFAULT_DURATION,
    DEFAULT_LANGUAGE,
    DEFAULT_TRANSITION,
    DEFAULT_VIDEO_FORMAT,
    ENABLE_SCRIPT_REVIEW,
    ENABLE_SFX,
    ENABLE_AUTO_DUCKING,
    ENABLE_HOOK_TITLE,
    LLM_PROVIDER,
    MEDIA_PROVIDER,
    RANDOM_STYLE,
    SHUFFLE_MUSIC,
    SUBTITLE_DYNAMIC,
    SUBTITLE_HIGHLIGHT_COLOR,
    SUBTITLE_ANIMATION,
    SUBTITLE_MAX_WORDS,
    SUPPORTED_LANGUAGES,
    SUPPORTED_TRANSITIONS,
    VIDEO_CRF,
    VIDEO_PRESET,
    ENABLE_BROLL_SPLIT,
    ENABLE_PUNCH_IN,
    get_language_voice,
    sanitize_env_value,
)


def parse_args() -> argparse.Namespace:
    """Parse and sanitize command-line arguments."""
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
        "--robo",
        action="store_true",
        help="Robo Agents mode: generate a humorous conversation between Orange and Blue robot agents."
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target historical date in NASA archive (format: YYYY-MM-DD, e.g. '2024-04-08', '2015-07-14', back to June 1995)."
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=None,
        help="Navigate N days into the past to discover NASA astronomy events from that time window (e.g. 30, 90, 365)."
    )
    parser.add_argument(
        "--archive", "--random-date",
        dest="archive",
        action="store_true",
        help="Explore legendary gems and historic discoveries randomly chosen from NASA's 30-year APOD archive (1995 to present)."
    )
    parser.add_argument(
        "--no-badge-date",
        action="store_true",
        help="Disable displaying the capture/publication date on the video attribution badge."
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
        choices=["auto", "nasa", "pexels", "pixabay", "pollinations"],
        help="Media source provider:\n"
             "  'auto'         : Intelligent cascade (NASA -> Pexels -> Pixabay -> Pollinations FLUX)\n"
             "  'pollinations' : Pollinations.ai FLUX (Photorealistic AI text-to-image generation for impossible visuals)\n"
             "  'nasa'         : Official NASA Image & Video Library (public domain space media)\n"
             "  'pexels'       : Pexels API (high-definition vertical 9:16 stock videos & photos)\n"
             "  'pixabay'      : Pixabay API (space animations, 3D CGI simulations & stock footage)"
    )
    parser.add_argument(
        "--pollinations-key",
        type=str,
        default=None,
        help="Optional Pollinations API key (from enter.pollinations.ai) to increase concurrency limits."
    )
    parser.add_argument(
        "--pollinations-model",
        type=str,
        default=None,
        choices=["flux", "turbo", "sana"],
        help="Pollinations text-to-image model (default: flux, with fallback to turbo)."
    )
    parser.add_argument(
        "--ai-fallback",
        dest="ai_fallback",
        action="store_true",
        default=True,
        help="Enable Pollinations FLUX text-to-image fallback when stock video/photo libraries yield no direct match (default: active)."
    )
    parser.add_argument(
        "--no-ai-fallback",
        dest="ai_fallback",
        action="store_false",
        help="Disable AI image generation fallback (uses synthetic background color instead)."
    )
    parser.add_argument(
        "--pexels-key",
        type=str,
        default=None,
        help="Custom Pexels API key (or set PEXELS_API_KEY in .env file)"
    )
    parser.add_argument(
        "--pixabay-key",
        type=str,
        default=None,
        help="Custom Pixabay API key (or set PIXABAY_API_KEY in .env file)"
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
        "--review",
        dest="review",
        action="store_true",
        default=ENABLE_SCRIPT_REVIEW,
        help="Enable optional secondary LLM Critic/Reviewer Agent pass (default: False for fastest direct generation)"
    )
    parser.add_argument(
        "--no-review",
        dest="review",
        action="store_false",
        help="Disable secondary script review agent for direct 1-pass generation (default)"
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
        "--music-volume",
        type=float,
        default=None,
        help="Background music volume ratio (0.0 to 1.0, default: 0.22 / 22%%)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep intermediate scene clips and audio files in temp/ directory"
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=VIDEO_CRF,
        help=f"Video quality Constant Rate Factor (16-23, default: {VIDEO_CRF}; lower means higher quality)"
    )
    parser.add_argument(
        "--preset",
        type=str,
        default=VIDEO_PRESET,
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"],
        help=f"FFmpeg compression preset (default: '{VIDEO_PRESET}')"
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
    # Viral retention & pacing options
    parser.add_argument(
        "--broll-split",
        dest="broll_split",
        action="store_true",
        default=ENABLE_BROLL_SPLIT,
        help="Split long scenes (>3.5s) into two visual cuts to maintain 2.5s pacing (default: active)"
    )
    parser.add_argument(
        "--no-broll-split",
        dest="broll_split",
        action="store_false",
        help="Disable automatic B-Roll splitting of long scenes"
    )
    parser.add_argument(
        "--punch-in",
        dest="punch_in",
        action="store_true",
        default=ENABLE_PUNCH_IN,
        help="Apply Pattern Interrupt snap punch-in zoom during first 0.4s of Scene 1 (default: active)"
    )
    parser.add_argument(
        "--no-punch-in",
        dest="punch_in",
        action="store_false",
        help="Disable opening hook punch-in zoom"
    )
    # Subtitle options
    parser.add_argument(
        "--subtitle-margin", "--sub-margin",
        dest="subtitle_margin",
        type=int,
        default=None,
        help="Custom bottom margin for subtitles in pixels (default: auto per format, e.g. 540 for vertical Shorts Safe Zone)"
    )
    parser.add_argument(
        "--subtitle-color", "--color",
        type=str,
        default=SUBTITLE_HIGHLIGHT_COLOR,
        help=f"Active subtitle highlight color ('random', {', '.join(repr(k) for k in CURATED_SUBTITLE_COLORS.keys())}, or custom hex; default: '{SUBTITLE_HIGHLIGHT_COLOR}')"
    )
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
    parser.add_argument(
        "--subtitle-animation", "--sub-anim",
        dest="subtitle_animation",
        choices=["pop", "none"],
        default=SUBTITLE_ANIMATION,
        help=f"Subtitle animation entrance style ('pop' for energetic bounce, 'none' for instant cut; default: '{SUBTITLE_ANIMATION}')"
    )
    parser.add_argument(
        "--subtitle-words", "--sub-words",
        dest="subtitle_words",
        type=int,
        default=None,
        help=f"Target words per subtitle line (default: {SUBTITLE_MAX_WORDS} for vertical mobile video, 5 for horizontal)"
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
    parser.add_argument(
        "--random-sfx",
        action="store_true",
        default=True,
        help="Enable dynamic acoustic variations for sound effects (default: True)"
    )
    parser.add_argument(
        "--no-random-sfx",
        action="store_true",
        help="Disable SFX acoustic variations (use fixed static waveforms)"
    )
    # Variety and Randomization options
    parser.add_argument(
        "--random-style", "--variety",
        action="store_true",
        default=RANDOM_STYLE,
        help="Enable full style randomization (random curated subtitle highlight color, randomized transitions, varied SFX, and shuffled music)"
    )
    parser.add_argument(
        "--shuffle-music",
        action="store_true",
        default=SHUFFLE_MUSIC,
        help="Randomly select background music from assets/music/ if multiple tracks exist (default: True)"
    )
    parser.add_argument(
        "--no-shuffle-music",
        action="store_true",
        help="Disable music shuffling and use standard background.mp3"
    )
    parser.add_argument(
        "--auto-ducking",
        action="store_true",
        default=ENABLE_AUTO_DUCKING,
        help="Enable dynamic sidechain auto-ducking (music automatically ducks when voice speaks and swells in pauses) (default: True)"
    )
    parser.add_argument(
        "--no-auto-ducking",
        action="store_true",
        help="Disable dynamic sidechain auto-ducking (use static flat music volume)"
    )
    # Attribution badge display options
    parser.add_argument(
        "--no-badge-label",
        action="store_true",
        help="Disable displaying the visual subject label in attribution badges"
    )
    # Hook Title Overlay options (High-retention opening card)
    parser.add_argument(
        "--hook-title",
        type=str,
        default=None,
        help="Custom viral headline text displayed during seconds 0-2.5 (default: auto-extracted from script title/hook)"
    )
    parser.add_argument(
        "--no-hook-title",
        action="store_true",
        default=not ENABLE_HOOK_TITLE,
        help="Disable the viral Hook Title overlay on the first scene"
    )

    # Custom Script Option (Pre-edited scenes JSON)
    parser.add_argument(
        "--script", "--custom-script",
        dest="custom_script",
        type=str,
        default=None,
        help="Path to an existing pre-edited script JSON file (e.g. output/<video>/script.json). Skips AI generation and uses your edited scenes directly."
    )

    # Tester & Audit Mode Options
    parser.add_argument(
        "--audit", "--tester", "--test-mode",
        dest="audit",
        action="store_true",
        help="Interactive Tester & Audit Mode: Review script, audio, and downloaded visual media in console and HTML storyboard before rendering. Allows replacing assets or editing narration."
    )
    parser.add_argument(
        "--dry-run", "--no-render",
        dest="dry_run",
        action="store_true",
        help="Dry-Run Mode: Generates script, audio narration, downloads visuals, and creates HTML storyboard, but skips final video rendering."
    )
    parser.add_argument(
        "--audit-html",
        type=str,
        default=None,
        help="Custom file path for the exported HTML visual storyboard (default: output/<video>/storyboard_audit.html or assets/storyboard_audit.html)"
    )

    args = parser.parse_args()

    # Sanitize inputs (strip surrounding quotes or comments if passed from shell, env, or docker)
    args.language = (args.language or DEFAULT_LANGUAGE).lower().strip()
    args.voice = get_language_voice(args.language, sanitize_env_value(args.voice) if args.voice else None)
    if args.pexels_key:
        args.pexels_key = sanitize_env_value(args.pexels_key)
    if args.pixabay_key:
        args.pixabay_key = sanitize_env_value(args.pixabay_key)
    if args.groq_key:
        args.groq_key = sanitize_env_value(args.groq_key)
    if args.gemini_key:
        args.gemini_key = sanitize_env_value(args.gemini_key)
    if args.openai_key:
        args.openai_key = sanitize_env_value(args.openai_key)

    # Auto-detect if user passed a numeric topic (e.g. --topic 2 or --topic "2" meaning option #2)
    if args.topic and args.topic.strip().isdigit() and 1 <= int(args.topic.strip()) <= 20:
        args.top_choice = int(args.topic.strip())
        args.trending = True
        args.topic = None

    # If --top-choice was explicitly passed in command line arguments, activate trending mode
    if any(arg.startswith("--top-choice") for arg in sys.argv):
        args.trending = True

    # Auto-activate trending if historical date/days-back/archive is specified without a custom topic
    if (args.date or args.days_back or args.archive) and not args.topic and not args.discover:
        args.trending = True

    # Handle Variety / Randomization overrides
    if args.random_style:
        if not args.no_transitions and args.transition == DEFAULT_TRANSITION:
            args.transition = "random"
        if args.subtitle_color == SUBTITLE_HIGHLIGHT_COLOR:
            args.subtitle_color = "random"
        args.shuffle_music = True
        args.random_sfx = True

    if args.no_shuffle_music:
        args.shuffle_music = False

    if args.no_random_sfx:
        args.random_sfx = False

    return args
