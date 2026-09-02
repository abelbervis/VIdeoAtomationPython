"""
Decoupled Text-to-Speech (TTS) Provider.
Supports Microsoft Edge Neural TTS, OpenAI TTS, Google TTS, and scene-level synchronization.
Generates high quality scientific documentary narration with precise timestamps.
"""

import abc
import asyncio
import json
import os
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import AUDIO_DIR, TTS_PROVIDER, TTS_API_KEY, DEFAULT_TTS_VOICE, OPENAI_API_KEY
from utils.files import get_media_duration


class BaseTTSProvider(abc.ABC):
    """Abstract base class for TTS engines."""

    @abc.abstractmethod
    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        """Synthesize text into an audio file."""
        pass


class EdgeTTSProvider(BaseTTSProvider):
    """Microsoft Edge Neural TTS (Free, high-grade documentary quality voices)."""

    def __init__(self, default_voice: str = DEFAULT_TTS_VOICE):
        self.default_voice = default_voice

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        selected_voice = voice or self.default_voice
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Try python edge-tts library if installed
        try:
            import edge_tts

            async def _run():
                communicate = edge_tts.Communicate(text, selected_voice)
                await communicate.save(str(output_path))

            asyncio.run(_run())
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        except ImportError:
            pass
        except Exception as e:
            print(f"  ⚠️ edge-tts python call error: {e}")

        # 2. Try edge-tts CLI tool if available
        try:
            cmd = ["edge-tts", "--voice", selected_voice, "--text", text, "--write-media", str(output_path)]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        except Exception:
            pass

        return False


class OpenAITTSProvider(BaseTTSProvider):
    """OpenAI TTS API."""

    def __init__(self, api_key: str = OPENAI_API_KEY):
        self.api_key = api_key

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = "onyx") -> bool:
        if not self.api_key:
            return False

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": voice or "onyx"  # Onyx or alloy fits documentary
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/audio/speech",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(output_path, "wb") as f:
                f.write(response.read())

            return output_path.exists() and output_path.stat().st_size > 0
        except Exception as e:
            print(f"  ⚠️ OpenAI TTS error: {e}")
            return False


class GoogleTTSProvider(BaseTTSProvider):
    """Google Translate TTS (REST client fallback for zero-key immediate audio)."""

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Split long text if necessary
        text_encoded = urllib.parse.quote(text[:200])
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text_encoded}&tl=es&client=tw-ob"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=15) as response, open(output_path, "wb") as f:
                f.write(response.read())

            return output_path.exists() and output_path.stat().st_size > 0
        except Exception as e:
            print(f"  ⚠️ Google TTS error: {e}")
            return False


class SyntheticFallbackTTSProvider(BaseTTSProvider):
    """Generates clean synthetic speech audio via FFmpeg / eSpeak fallback if offline."""

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Try espeak if installed
        try:
            cmd = ["espeak", "-v", "es", "-w", str(output_path), text]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        except Exception:
            pass

        # Minimum emergency fallback: estimate duration by word count and generate silent audio track with tone
        words = len(text.split())
        est_duration = max(3.0, words / 2.5)
        try:
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-t", str(est_duration),
                "-q:a", "9",
                "-acodec", "libmp3lame",
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except Exception:
            return False


class TTSManager:
    """Manages narration generation, scene audio synchronization, and combined narration."""

    def __init__(self, provider_type: str = TTS_PROVIDER, voice: str = DEFAULT_TTS_VOICE):
        self.voice = voice
        self.providers: List[BaseTTSProvider] = []

        # Setup primary provider
        if provider_type == "openai" and OPENAI_API_KEY:
            self.providers.append(OpenAITTSProvider())
        elif provider_type == "edge":
            self.providers.append(EdgeTTSProvider(voice))

        # Add standard fallbacks
        self.providers.append(EdgeTTSProvider(voice))
        self.providers.append(GoogleTTSProvider())
        self.providers.append(SyntheticFallbackTTSProvider())

    def synthesize_script(
        self,
        script: Dict[str, Any],
        output_dir: Path = AUDIO_DIR
    ) -> Tuple[Path, List[Dict[str, Any]], float]:
        """
        Synthesize audio for each scene in the script.
        Returns:
            - combined_audio_path: Path to narration.mp3
            - scene_timings: List of scene timing data (start, end, duration, narration)
            - total_duration: float
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        scenes = script.get("scenes", [])
        scene_files: List[Path] = []
        scene_timings: List[Dict[str, Any]] = []
        current_time = 0.0

        print("\n🎙️ Synthesizing narration for each scene...")

        for idx, scene in enumerate(scenes, start=1):
            narration = scene.get("narration", "").strip()
            scene_audio_path = output_dir / f"scene_{idx:02d}.mp3"

            success = False
            for provider in self.providers:
                if provider.synthesize_text(narration, scene_audio_path, self.voice):
                    success = True
                    break

            if not success or not scene_audio_path.exists():
                print(f"  ⚠️ Failed to synthesize audio for scene {idx}, generating placeholder timing.")
                # Generate emergency silent audio
                SyntheticFallbackTTSProvider().synthesize_text(narration, scene_audio_path)

            duration = get_media_duration(scene_audio_path)
            duration = max(duration, 3.0)  # Guarantee minimum readable scene duration

            timing = {
                "scene_id": idx,
                "narration": narration,
                "start": round(current_time, 2),
                "end": round(current_time + duration, 2),
                "duration": round(duration, 2),
                "audio_file": scene_audio_path
            }
            scene_timings.append(timing)
            scene_files.append(scene_audio_path)
            current_time += duration
            print(f"  ✅ Scene {idx:02d}: {duration:.1f}s — \"{narration[:45]}...\"")

        # Combine all scene audios into narration.mp3
        combined_audio_path = output_dir / "narration.mp3"
        self._concat_audios(scene_files, combined_audio_path)

        total_duration = get_media_duration(combined_audio_path)
        if total_duration <= 0:
            total_duration = current_time

        print(f"🎵 Full narration generated: {combined_audio_path.name} ({total_duration:.1f}s)")
        return combined_audio_path, scene_timings, total_duration

    def _concat_audios(self, audio_files: List[Path], output_path: Path) -> None:
        """Concatenate MP3 scene audios using FFmpeg."""
        concat_list_file = output_path.parent / "audio_concat.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for af in audio_files:
                f.write(f"file '{af.resolve()}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c", "copy",
            str(output_path)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            # Re-encode if stream copy fails
            cmd_reencode = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_file),
                "-acodec", "libmp3lame",
                "-b:a", "192k",
                str(output_path)
            ]
            subprocess.run(cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        concat_list_file.unlink(missing_ok=True)
