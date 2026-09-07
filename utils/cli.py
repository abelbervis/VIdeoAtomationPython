"""
Command-Line Interface (CLI) Parser for Science & Stock Shorts Generator.
Defines all CLI flags, descriptions, defaults, and input sanitization.
"""

import argparse
import sys
from typing import Any

from config import (
    DEFAULT_DURATION,
    DEFAULT_LANGUAGE,
    DEFAULT_TRANSITION,
    DEFAULT_VIDEO_FORMAT,
    ENABLE_SFX,
    LLM_PROVIDER,
    MEDIA_PROVIDER,
    SUBTITLE_DYNAMIC,
    SUPPORTED_LANGUAGES,
    SUPPORTED_TRANSITIONS,
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
    # Attribution badge display options
    parser.add_argument(
        "--no-badge-label",
        action="store_true",
        help="Disable displaying the visual subject label in attribution badges"
    )

    args = parser.parse_args()

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

    return args
