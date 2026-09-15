"""
Robo Agents Pipeline Runner.
CLI runner for creating dual-robot humorous short videos.
"""

import sys
import time
from pathlib import Path

from ai.robo_generator import RoboScriptGenerator
from audio.robo_tts import RoboTTSManager
from config import PEXELS_API_KEY, PIXABAY_API_KEY
from providers.pexels import PexelsProvider
from providers.pixabay import PixabayProvider
from utils.files import check_ffmpeg
from video.robo_render import RoboRenderer


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
