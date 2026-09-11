"""
Main entry point for Robo Agents Video Generator.
CLI runner for creating dual-robot humorous short videos.
"""

import argparse
import sys
import time
from pathlib import Path

from config import PEXELS_API_KEY, PIXABAY_API_KEY
from providers.pexels import PexelsProvider
from providers.pixabay import PixabayProvider
from robo_agents.renderer import RoboRenderer
from robo_agents.script_generator import RoboScriptGenerator
from robo_agents.tts_manager import RoboTTSManager
from utils.files import check_ffmpeg


def parse_args():
    parser = argparse.ArgumentParser(
        description="Robo Agents Shorts Generator - Animated dual-robot dialogue videos."
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="por qué el cielo es azul",
        help="Topic for the humorous conversation between Orange and Blue robots.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=5,
        help="Number of dialogue turns (default: 5).",
    )
    parser.add_argument(
        "--orange-voice",
        type=str,
        default="es-MX-JorgeNeural",
        help="Edge TTS voice for Orange Robot (Charismatic).",
    )
    parser.add_argument(
        "--blue-voice",
        type=str,
        default="es-ES-AlvaroNeural",
        help="Edge TTS voice for Blue Robot (Scientist).",
    )
    parser.add_argument(
        "--pexels-key",
        type=str,
        default=PEXELS_API_KEY,
        help="Pexels API Key for background stock videos.",
    )
    parser.add_argument(
        "--pixabay-key",
        type=str,
        default=PIXABAY_API_KEY,
        help="Pixabay API Key for background stock videos.",
    )
    return parser.parse_args()


def run_robo_pipeline(
    topic: str = "por qué el cielo es azul",
    turns: int = 5,
    orange_voice: str = "es-MX-JorgeNeural",
    blue_voice: str = "es-ES-AlvaroNeural",
    pexels_key: str = None,
    pixabay_key: str = None,
) -> Path:
    """Run full robo agents pipeline from topic to final MP4 video."""
    start_time = time.time()

    if not check_ffmpeg():
        print("❌ Error: FFmpeg is required but was not found in PATH.")
        sys.exit(1)

    print("=" * 65)
    print("🤖 ROBO AGENTS VIDEO GENERATOR | Dual-Robot Dialogue Engine")
    print("=" * 65)
    print(f"🎯 Topic:        '{topic}'")
    print(f"💬 Turns:        {turns}")
    print(f"🟧 Orange Voice: {orange_voice}")
    print(f"🟦 Blue Voice:   {blue_voice}")
    print("=" * 65)

    # 1. Generate Dialogue Script
    script_gen = RoboScriptGenerator()
    script = script_gen.generate_script(topic, num_turns=turns)

    # 2. Synthesize Audio for each Turn
    tts_mgr = RoboTTSManager(orange_voice=orange_voice, blue_voice=blue_voice)
    turn_data = tts_mgr.synthesize_dialogue(script.get("turns", []))

    # 3. Media Providers for Background Videos
    pexels = PexelsProvider(api_key=pexels_key or PEXELS_API_KEY)
    pixabay = PixabayProvider(api_key=pixabay_key or PIXABAY_API_KEY)

    # 4. Render Scene Clips
    renderer = RoboRenderer(pexels_provider=pexels, pixabay_provider=pixabay)

    print("\n🎨 Rendering animated turn clips with speech bubbles...")
    clip_files = []
    for idx, turn in enumerate(turn_data, start=1):
        print(f"  🎬 Rendering turn {idx}/{len(turn_data)} [{turn['speaker'].upper()}]: '{turn['text'][:30]}...'")
        clip_path = renderer.render_turn_clip(turn, idx)
        clip_files.append(clip_path)

    # 5. Assemble Final MP4 Video
    final_video = renderer.assemble_final_video(clip_files, topic)

    elapsed = time.time() - start_time
    print(f"✨ Total generation time: {elapsed:.2f} seconds.")
    return final_video


def main():
    args = parse_args()
    run_robo_pipeline(
        topic=args.topic,
        turns=args.turns,
        orange_voice=args.orange_voice,
        blue_voice=args.blue_voice,
        pexels_key=args.pexels_key,
        pixabay_key=args.pixabay_key,
    )


if __name__ == "__main__":
    main()
