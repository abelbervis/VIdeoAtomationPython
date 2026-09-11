"""
Edge TTS Synthesis Manager for Robo Agents.
Provides distinct character voices for Orange Robot (charismatic) and Blue Robot (scientist).
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from config import AUDIO_DIR, TEMP_DIR
from utils.files import get_media_duration

# Default distinct Edge-TTS voices
DEFAULT_ORANGE_VOICE = "es-MX-JorgeNeural"  # Energetic, charismatic male voice
DEFAULT_BLUE_VOICE = "es-ES-AlvaroNeural"    # Intellectual, scientific Spanish voice


class RoboTTSManager:
    """Handles multi-character TTS synthesis using Microsoft Edge Neural TTS."""

    def __init__(self, orange_voice: str = DEFAULT_ORANGE_VOICE, blue_voice: str = DEFAULT_BLUE_VOICE):
        self.orange_voice = orange_voice
        self.blue_voice = blue_voice

    def synthesize_turn(self, text: str, speaker: str, output_path: Path) -> float:
        """
        Synthesize spoken text for a specific speaker ('orange' or 'blue').
        Returns the exact duration of the synthesized audio clip in seconds.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        voice = self.orange_voice if speaker.lower() == "orange" else self.blue_voice

        # 1. Try python edge-tts library
        success = False
        try:
            import edge_tts

            async def _run():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(str(output_path))

            asyncio.run(_run())
            if output_path.exists() and output_path.stat().st_size > 0:
                success = True
        except Exception as e:
            pass

        # 2. Try CLI fallback if python import failed
        if not success:
            try:
                cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(output_path)]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                if output_path.exists() and output_path.stat().st_size > 0:
                    success = True
            except Exception:
                pass

        # 3. Fallback dummy audio generator if offline/edge-tts fails
        if not success or not output_path.exists():
            print(f"  ⚠️ Edge TTS synthesis failed for turn: '{text[:20]}...'. Creating silent placeholder clip.")
            # Calculate estimated reading duration (~15 chars per sec, min 2.5s)
            est_dur = max(2.5, len(text) / 15.0)
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-t", f"{est_dur:.2f}", str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        duration = get_media_duration(output_path)
        return duration if duration > 0 else 3.0

    def synthesize_dialogue(self, turns: List[Dict[str, Any]], temp_dir: Path = TEMP_DIR) -> List[Dict[str, Any]]:
        """
        Synthesizes audio for all turns in a dialogue script.
        Appends 'audio_path' and 'duration' to each turn dict.
        """
        print("🎙️ Synthesizing Robo dialogue audio clips with Edge TTS...")
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        synthesized_turns = []
        for turn in turns:
            turn_id = turn.get("turn_id", len(synthesized_turns) + 1)
            speaker = turn.get("speaker", "orange")
            text = turn.get("text", "")

            audio_file = temp_dir / f"robo_turn_{turn_id:02d}_{speaker}.mp3"
            duration = self.synthesize_turn(text, speaker, audio_file)

            turn_copy = dict(turn)
            turn_copy["audio_path"] = str(audio_file)
            turn_copy["duration"] = duration
            synthesized_turns.append(turn_copy)
            print(f"  🔊 Turn {turn_id:02d} [{speaker.upper()}]: '{text[:30]}...' ({duration:.2f}s)")

        return synthesized_turns
